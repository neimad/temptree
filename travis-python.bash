TRAVIS_PYTHON_VERSION="0.1.0"

print_info() {
    # print_info MESSAGE
    #
    # Prints the given MESSAGE to the standard ouput stream in cyan.
    #
    local -r message="${*:?MESSAGE must be specified}"

    echo -e "\033[0;33m$message\033[0m"
}

print_success() {
    # print_success MESSAGE
    #
    # Prints the given MESSAGE to the standard ouput stream in green.
    #
    local -r message="${*:?MESSAGE must be specified}"

    echo -e "\033[0;32m$message\033[0m"
}

print_error() {
    # print_error MESSAGE
    #
    # Prints the given error MESSAGE to the standard error stream in red.
    #
    local -r message="${*:?MESSAGE must be specified}"

    echo -e "\033[0;31m$message\033[0m" >&2
    return 1
}

trim() {
    # trim STRING
    #
    # Trims leading and trailing whitespace characters from STRING.
    #
    local string="${1:?STRING must be specified}"

    shopt -s extglob
    string=${string##+([[:space:]])}
    string=${string%%+([[:space:]])}

    echo "$string"
}

abspath() {
    # abspath PATH
    #
    # Gives the absolute path from PATH.
    #
    # Borrowed from https://stackoverflow.com/a/23002317/427157.
    #
    local -r path="${1:?PATH must be specified}"
    local absolute

    if [[ -d $path ]]; then
        # The given path leads to a directory
        absolute=$(
            cd "$path" || return
            pwd
        )
    elif [[ -f $path ]]; then
        # The given path leads to a file
        if [[ $path == /* ]]; then
            # This path is already absolute
            absolute="$path"
        elif [[ $path == */* ]]; then
            # This path is relative and has multiple components
            absolute=$(
                cd "${path%/*}" || return
                pwd
            )/${path##*/}
        else
            # This path is relative and has a single component
            absolute="$PWD/$path"
        fi
    fi

    if [[ -z $absolute ]]; then
        print_error "Cannot make path absolute: File not found: $path"
        return 1
    fi

    echo "$absolute"
}

windows_path() {
    # windows_path PATH
    #
    # Converts a Unix PATH to Windows flavor.
    #
    local -r path="${1:?PATH must be specified}"
    local converted
    local parts

    # Convert slashes to backslashes
    converted="${path//\//\\}"

    if [[ $converted == \\* ]]; then
        # If it is an absolute path, convert the first component to a drive letter
        IFS=\\ read -ra parts <<<"$converted"
        unset "parts[0]"
        parts[1]="${parts[1]^}:"

        OLDIFS=$IFS
        IFS=\\
        converted="${parts[*]}"
        IFS=$OLDIFS
    fi

    echo "$converted"
}

latest_version() {
    # latest_version SPECIFIER VERSIONS
    #
    # Gives the latest version matching the SPECIFIER from a list of VERSIONS.
    #
    # The versions are expected to follow the *semver* specification. The
    # REQUESTED version can be a complete version (major.minor.patch) or omit
    # one or more leading components.
    #
    local -r specifier="${1:?SPECIFIER version must be specified}"
    shift
    local -r versions=("${@:?VERSIONS must be specified}")
    local found_version=""

    for version in "${versions[@]}"; do
        if [[ $version == ${specifier}?(.[0-9]) && $version > $found_version ]]; then
            found_version="$version"
        fi
    done

    [[ -n $found_version ]] || return

    echo "$found_version"
}

git_update_repo() {
    # git_update_repo URL DIRECTORY
    #
    # Updates the Git repository located at DIRECTORY from the specified URL.
    #
    # If the repository doesn't exists, it is cloned from the specified URL.
    # Otherwise, it is fetched.
    # Then, the latest tag is checked out.
    #
    local -r url="${1:?Repository URL must be specified}"
    local -r directory="${2:?Clone DIRECTORY must be specified}"
    local -r original_working_directory="$PWD"

    if [[ ! -d $directory ]]; then
        git clone "$url" "$directory"
    fi

    cd "$directory" || return
    git fetch || return

    local -r latest_tag=$(git describe --abbrev=0 --tags)
    git config advice.detachedHead false # Prevents Git advice about detached head
    git checkout "$latest_tag"

    cd "$original_working_directory" || return
}

install_pyenv() {
    # install_pyenv LOCATION
    #
    # Installs pyenv to the specified LOCATION.
    #
    # The pyenv distribution is cloned from its Git repository and the latest
    # release is fetched.
    #
    # The `PATH` is updated to include the pyenv distribution and the shell
    # commands hash table is reset.
    #
    # The `PYENV_ROOT` environment variable is set to LOCATION.
    #
    local location="${1:?Installation LOCATION must be specified}"
    local -r repo_url="https://github.com/pyenv/pyenv"
    export PYENV_ROOT
    export PATH

    print_info "Installing latest pyenv to $location..."
    git_update_repo $repo_url "$location" || return

    PYENV_ROOT=$(abspath "$location")
    PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
    hash -r
}

available_python_versions_with_pyenv() {
    # available_python_versions_with_pyenv
    #
    # Gives the list of Python versions available via pyenv.
    #
    local versions
    local versions=()

    while IFS='' read -r version; do
        version=$(trim "$version")

        versions=("$version" "${versions[@]}")
    done < <(pyenv install --list)

    echo "${versions[@]}"
}

available_python_versions_with_chocolatey() {
    # available_python_versions_with_chocolatey
    #
    # Gives the list of Python versions available via Chocolatey.
    #
    local output
    local version
    local versions=()

    output=$(choco list python --exact --all-versions --limit-output)

    while read -r version; do
        version="${version#'python|'}"
        version=$(trim "$version")

        versions=("$version" "${versions[@]}")
    done <<<"$output"

    echo "${versions[@]}"
}

install_python() {
    # install_python LOCATION SPECIFIER
    #
    # Installs the latest Python version matching the specified one in the
    # specified LOCATION.
    #
    # The VERSION can be a complete version (major.minor.patch) or omit one or
    # more leading components.
    #
    # When OS is Linux or macOS, pyenv is used, on Windows, Chocolatey is used.
    #
    local -r location="${1:?installation LOCATION must be given}"
    local -r specifier="${2:?SPECIFIER must be given}"
    local -a available_versions
    local version
    export PATH

    if [[ $TRAVIS_OS_NAME == "windows" ]]; then
        # shellcheck disable=SC2207
        available_versions=($(available_python_versions_with_chocolatey))
    else
        install_pyenv "$location"
        print_success "Installed $(pyenv --version)."

        IFS=" " read -ra available_versions <<<"$(available_python_versions_with_pyenv)"
    fi

    version=$(latest_version "$specifier" "${available_versions[@]}")

    if [[ -z $version ]]; then
        print_error "No Python version found matching $specifier"
        return 1
    fi

    print_info "Installing Python $version..."

    if [[ $TRAVIS_OS_NAME == "windows" ]]; then
        choco install python \
            --version="$version" \
            --yes \
            --install-arguments="/quiet InstallAllUsers=0 TargetDir=\"$(windows_path "$location")\"" \
            --override-arguments \
            --apply-install-arguments-to-dependencies

        PATH="$location:$location/Scripts:$PATH"
        hash -r
    else
        pyenv install --skip-existing "$version"
        pyenv global "$version"
        pyenv rehash
    fi

    print_success "Installed $(python --version)."
}

__travis_python_setup() {
    # __travis_python_setup
    #
    # Setup Python tools for Travis CI.
    #
    print_info "travis-python ${TRAVIS_PYTHON_VERSION}"

    : "${TRAVIS_OS_NAME:?must be set and not null}"

    if [[ ${TRAVIS_OS_NAME} == "windows" ]]; then
        # Workaround for https://github.com/chocolatey/choco/issues/1843
        choco upgrade chocolatey --yes --version 0.10.13 --allow-downgrade
        print_success "Installed Chocolatey $(choco --version)."
    fi

    print_success "Python tools for Travis CI loaded."
}

__travis_python_setup
