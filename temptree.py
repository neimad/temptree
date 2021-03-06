# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright © 2019 Damien Flament
# This file is part of temptree.

"""Generates temporary files and directories from a tree.

[![Build Status][ci-badge]][ci]
[![PyPI][pypi-badge]][package]
[![Python Version][py-versions-badge]][package]
[![License][license-badge]][GNU GPL 3 or later]

The provided `TemporaryTree` class allows to create complete files hierarchies
under a root `tempfile.TemporaryDirectory`.

It is well suited for usage within *doctests* :

    >>> from temptree import TemporaryTree

    >>> with TemporaryTree(["foo.py", "bar.py"]) as root:
    ...     (root / "foo.py").is_file()
    ...     (root / "bar.py").is_file()
    ...
    True
    True

A complete file hierarchy can be easily created, including text files content
and files mode:

    >>> with TemporaryTree({
    ...     "foo.py": ('''
    ...     import os
    ...     import sys
    ...
    ...     FOO = "foo"
    ...     ''', 0o700),
    ...     "bar": {
    ...         "bar.py": '''
    ...         import foo
    ...         import pathlib
    ...
    ...         def bar():
    ...             return foo.FOO
    ...         ''',
    ...         "baz.py": None,
    ...     }
    ... }) as root:
    ...     (root / "foo.py").exists()
    ...     (root / "bar").is_dir()
    ...     (root / "bar" / "bar.py").is_file()
    ...     (root / "bar" / "baz.py").is_file()
    ...
    True
    True
    True
    True

Installation
------------

Add `temptree` to your project dependencies:

    poetry add temptree

If you just need it within your *doctests*, add it as a development dependency:

    poetry add --dev temptree

Documentation
-------------

[The complete documentation] is available from Github Pages.

Development
-----------

The development tasks are managed using [Invoke]. Use it to list the available
tasks:

    poetry run invoke --list

Install the [pre-commit] hook within your repository:

    poetry run pre-commit install

Run the tests using [Pytest]:

    poetry run pytest

Contributing
------------

This project is hosted on a [Github repository].

If you're facing an issue using `temptree`, please look at
[the existing tickets]. Then you may open a new one.

You may also [make a push request] to help improve it.

Changelog
---------

See [the changelog] to see what changes have been made and what you can expect
in the next release.

License
-------

`temptree` is licensed under the [GNU GPL 3 or later].

[ci-badge]: https://img.shields.io/travis/neimad/temptree?style=flat-square
[pypi-badge]: https://img.shields.io/pypi/v/temptree?style=flat-square
[py-versions-badge]: https://img.shields.io/pypi/pyversions/temptree?style=flat-square
[license-badge]: https://img.shields.io/github/license/neimad/temptree?style=flat-square

[GNU GPL 3 or later]: https://github.com/neimad/temptree/blob/master/LICENSE.md
[the changelog]: https://github.com/neimad/temptree/blob/master/CHANGELOG.md
[The complete documentation]: https://neimad.github.io/temptree/
[Github repository]: https://github.com/neimad/temptree
[the existing tickets]: https://github.com/neimad/temptree/issues
[make a push request]: https://github.com/neimad/temptree/pulls
[package]: https://pypi.org/project/temptree/
[ci]: https://travis-ci.org/neimad/temptree

[Invoke]: https://pyinvoke.org
[pre-commit]: https://pre-commit.com
[Pytest]: https://pytest.org

"""

import os
from pathlib import Path
from tempfile import TemporaryDirectory


class TemporaryTree(object):
    """A tree of files and directories located in a `pathlib.TemporaryDirectory`.

    To build a list of files, just specify their names in a list:

    >>> with TemporaryTree(["foo.py", "bar.py"]) as root:
    ...     (root / "foo.py").is_file()
    ...     (root / "bar.py").is_file()
    ...
    True
    True

    To build a hierarchy of files and directories, use nested dictionnaries:

    >>> tree = TemporaryTree({
    ...     "foo.py": None,
    ...     "bar.py": None,
    ...     "baz": {
    ...         "foo.cfg": None,
    ...         "bar.ini": None
    ...     }
    ... })
    ...

    A temporary directory is created and is available through the `TemporaryTree.root`
    attribute as a `pathlib.Path`:

        >>> from pathlib import Path
        >>> isinstance(tree.root, Path)
        True


    The specified files hierarchy is created under the root:

        >>> for f in sorted(tree.root.rglob("*")):
        ...     print(f.relative_to(tree.root))
        ...
        bar.py
        baz
        baz/bar.ini
        baz/foo.cfg
        foo.py

    The tree is cleaned up when the `TemporaryTree` instance is destructed:

        >>> root = tree.root
        >>> del tree
        >>> root.exists()
        False

    It can also be explicitly cleaned up using the `TemporaryTree.cleanup` method.

    Context manager
    ---------------

    A tree can be used as a context manager returning the root `pathlib.Path`:

        >>> with TemporaryTree({"foo.py": None}) as root:
        ...     foo = root / "foo.py"
        ...     foo.exists()
        ...
        True


    On context completion, the tree is cleaned up.

    Files content
    -------------
    The files text content can be given as a value within the files hierarchy
    specification dictionnary:

        >>> tree = TemporaryTree({"foo.py": '''
        ... FOO = "foo"
        ... '''})
        ...
        >>> foo = tree / "foo.py"
        >>> print(foo.read_text())
        <BLANKLINE>
        FOO = "foo"
        <BLANKLINE>

    Files mode and access flags
    ---------------------------

    The files mode can be specified as a value within the files hierarchy specification
    dictionnary:

        >>> tree = TemporaryTree({"foo.py": 0o700})
        >>> foo = tree / "foo.py"
        >>> format(foo.stat().st_mode, "o")
        '100700'

    Slash operator
    --------------

    The slash operator can be used in the same way as with `pathlib.Path` objects:

        >>> str(tree / "baz.py") == f"{str(tree.root)}/baz.py"
        True

    """

    def __init__(self, tree):
        self._root = TemporaryDirectory()

        _build_tree(self.root, tree)

    @property
    def root(self):
        """The root of the tree as a `pathlib.Path` object."""
        return Path(self._root.name)

    def __enter__(self):
        """Gives the root directory.

        Returns
        -------
            The tree root.

        """
        return self.root

    def __exit__(self, e_type, e_value, e_traceback):
        """Exits the context."""
        pass

    def __truediv__(self, other):
        """Uses the slash operator to create childs paths from the root."""
        return self.root.__truediv__(other)

    def cleanup(self):
        """Cleans up the tree.

        The root temporary directory is cleaned up:

            >>> tree = TemporaryTree({"foo.py": None})
            >>> tree.root.exists()
            True
            >>> tree.cleanup()
            >>> tree.root.exists()
            False

        """
        self._root.cleanup()

    def __repr__(self):
        """Represents the tree by the location of its root.

        The `TemporaryTree` is represented by the location of its root in the
        filesystem :

            >>> tree = TemporaryTree({})
            >>> repr(tree) == f"<TemporaryTree at {tree.root}>"
            True

        """
        class_name = self.__class__.__name__

        return f"<{class_name} at {str(self.root)}>"


class FilenameError(ValueError):
    """Inappropriate file name."""


def _check_filename(filename):
    r"""Checks if a filename is appropriate.

    Empty filenames are forbiden:

        >>> _check_filename("")
        Traceback (most recent call last):
        ...
        temptree.FilenameError: Can not create a file with an empty name

    Current directory as filename is forbiden:

        >>> from os import curdir

        >>> _check_filename(curdir)
        Traceback (most recent call last):
        ...
        temptree.FilenameError: Can not create a file whose name is `...`

    Parent directory as filename is forbiden:

        >>> from os import pardir

        >>> _check_filename(pardir)
        Traceback (most recent call last):
        ...
        temptree.FilenameError: Can not create a file whose name is `...`

    Filenames containing path components separator are forbiden:

        >>> from os import sep, altsep

        >>> _check_filename(sep)
        Traceback (most recent call last):
        ...
        temptree.FilenameError: Can not create a file whose name contains `...`

        >>> _check_filename(altsep) # doctest: +SKIP
        Traceback (most recent call last):
        ...
        temptree.FilenameError: Can not create a file whose name contains `...`

    Filenames containing a null byte are forbiden:

        >>> _check_filename("\0")
        Traceback (most recent call last):
        ...
        temptree.FilenameError: Can not create a file whose name contains a null byte

    """
    NULL_BYTE = "\0"

    if len(filename) == 0:
        raise FilenameError("Can not create a file with an empty name")

    if filename in (os.curdir, os.pardir):
        raise FilenameError(f"Can not create a file whose name is `{filename}`")

    if os.sep in filename:
        raise FilenameError(f"Can not create a file whose name contains `{os.sep}`")

    if os.altsep and os.altsep in filename:
        raise FilenameError(f"Can not create a file whose name contains `{os.altsep}`")

    if NULL_BYTE in filename:
        raise FilenameError(f"Can not create a file whose name contains a null byte")


def _build_tree(directory, tree):
    """Creates the files hierarchy specified by the tree.

    Files and directories specified by the `tree` dictionnary are created within the
    given directory.

    If the tree is a list, its element are taken as the keys in the tree dictionnary.

    If a value is a list or a dictionnary, it is taken as a subtree under a subdirectory
    whose the name is the related key.

    """
    if isinstance(tree, list):
        tree = {name: None for name in tree}

    for name, value in tree.items():
        _check_filename(name)

        if isinstance(value, (list, dict)):
            subdirectory = directory / name
            subdirectory.mkdir()

            assert subdirectory.exists()

            _build_tree(subdirectory, value)
        else:
            file = directory / name

            if value is None:
                value = (None, None)
            elif isinstance(value, (int, str)):
                value = (value, None)

            _create_file(file, value)

            assert file.exists()


def _create_file(file, specification):
    """Creates the file following the given specification.

    The `file` is created while following the `specification`.

        >>> from tempfile import TemporaryDirectory
        >>> from pathlib import Path

        >>> tempdir = TemporaryDirectory()
        >>> dir = Path(tempdir.name)
        >>> file = dir / "file"

        >>> file.exists()
        False
        >>> _create_file(file, (0o711, "file content"))
        >>> file.is_file()
        True
        >>> file.read_text()
        'file content'
        >>> format(file.stat().st_mode, "o")
        '100711'

    The specification must be an iterable containing:

     - the file mode as an integer,
     - the file content as a string.

    If the file mode is not specified, the default from `pathlib.Path.touch` is used:

        >>> file.unlink()
        >>> from os import umask

        >>> _create_file(file, (None, "file content"))
        >>> file.read_text()
        'file content'
        >>> file.stat().st_mode == 0o100666 - umask(0)
        True

    If the file content is not specified, it is left empty:

        >>> file.unlink()

        >>> _create_file(file, (0o711, None))
        >>> file.read_text()
        ''
        >>> format(file.stat().st_mode, "o")
        '100711'

    """
    content = None
    mode = None

    for value in specification:
        if isinstance(value, str):
            content = value
        elif isinstance(value, int):
            mode = value

    file.touch()

    if content:
        file.write_text(content)

    if mode:
        file.chmod(mode)
