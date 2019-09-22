from os import altsep, curdir, pardir, sep

from hypothesis import HealthCheck, given, settings
from hypothesis.strategies import (
    characters,
    composite,
    deferred,
    dictionaries,
    integers,
    lists,
    none,
    one_of,
    text,
)

from temptree import TemporaryTree


@composite
def filenames(draw):
    """Draws filenames.

    Filenames are draw as text not containing some forbiden characters.

    """
    forbiden_characters = []

    for string in (sep, altsep, curdir, pardir, "\0"):
        if string:
            if len(string) == 1 and string not in forbiden_characters:
                forbiden_characters.append(string)
            else:
                forbiden_characters.extend(
                    character
                    for character in string
                    if character not in forbiden_characters
                )

    return draw(
        text(
            alphabet=characters(
                blacklist_categories=("Cs",), blacklist_characters=forbiden_characters
            ),
            min_size=1,
            max_size=10,
        )
    )


@composite
def filenames_lists(draw):
    """Draws lists of filenames."""
    return draw(lists(filenames(), max_size=5))


@composite
def file_modes(draw):
    """Draws file modes.

    File modes are draw as integers between 0o000 and 0o777.

    """
    return draw(integers(min_value=0o000, max_value=0o777))


@composite
def file_contents(draw):
    """Draws file text content."""

    return draw(
        text(
            alphabet=characters(
                blacklist_categories=("Cs",), blacklist_characters=["\r"]
            ),
            max_size=20,
        )
    )


@composite
def file_specs(draw):
    """Draws file specifications.

    Files specifications are draw as a tuple of a file mode and file content, in any
    order and maybe null.

    """
    strategies = [none(), file_modes(), file_contents()]

    first = draw(one_of(*strategies))

    if first is None:
        pass
    elif isinstance(first, int):
        strategies.pop(1)
    elif isinstance(first, str):
        strategies.pop(2)
    else:
        raise Exception(f"Value `{first}` does not match a known strategy")

    second = draw(one_of(*strategies))

    return (first, second)


directory_specs = deferred(
    lambda: dictionaries(
        keys=filenames(),
        values=none()
        | file_modes()
        | file_contents()
        | file_specs()
        | filenames_lists()
        | directory_specs,
        max_size=5,
    )
)


trees = filenames_lists() | directory_specs


@settings(suppress_health_check=[HealthCheck.too_slow])
@given(tree=trees)
def test_temporary_tree(tree):
    def assert_on_tree(directory, tree):
        if isinstance(tree, list):
            tree = {name: None for name in tree}

        for name, value in tree.items():
            file = directory / name

            if isinstance(value, (list, dict)):
                assert file.is_dir()
                assert_on_tree(file, value)
            else:
                assert file.is_file()

                mode = None
                content = None

                if isinstance(value, int):
                    mode = value
                elif isinstance(value, str):
                    content = value

                if mode:
                    assert file.stat().st_mode == mode + 0o100000

                if content:
                    assert file.read_text() == content

    with TemporaryTree(tree) as root:
        assert root.is_dir()
        assert_on_tree(root, tree)
