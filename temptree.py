# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright © 2019 Damien Flament
# This file is part of temptree.

"""Generates temporary files and directories from a tree.

The provided `TemporaryTree` class allows to create complete files hierarchies under a
root `tempfile.TemporaryDirectory`.

It is well suited for usage within *doctests* :

    >>> from temptree import TemporaryTree
    >>> with TemporaryTree({
    ...     "foo.py": None,
    ...     "bar": {
    ...         "bar.py": None,
    ...         "baz.py": None,
    ...     }
    ... }) as root:
    ...     (root / "foo.py").exists()
    ...     (root / "bar").is_dir()
    ...     (root / "bar" / "bar.py").is_file()
    ...
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

[The complete documentation][documentation] is available from Github Pages.

Contributing
------------

This project is hosted on [Github][repository].

If you're facing an issue using `temptree`, please look at
[the existing tickets][issues]. Then you may open a new one.

You may also make a [push request][pull-requests] to help improve it.

License
-------

`temptree` is licensed under the [GNU GPL 3][GPL] or later.

[documentation]: https://neimad.github.io/temptree/
[repository]: https://github.com/neimad/temptree
[issues]: https://github.com/neimad/temptree/issues
[pull-requests]: https://github.com/neimad/temptree/pulls
[GPL]: https://www.gnu.org/licenses/gpl.html

"""

from pathlib import Path
from tempfile import TemporaryDirectory


class TemporaryTree(object):
    """A tree of files and directories located in a `pathlib.TemporaryDirectory`.

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

    Files mode and access flags
    ---------------------------

    The files mode can be specified as a value within the files hierarchy specification
    dictionnary:

        >>> tree = TemporaryTree({"foo.py": 0o700})
        >>> foo = tree.root / "foo.py"
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

        self._build(self.root, tree)

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

    def _build(self, directory, tree):
        """Creates the files and directories specified by the `tree` dictionnary.

        Parameters
        ----------
        directory: Path
            The directory to build the files hierarchy in.
        tree: dict
            The files hierarchy specification.

        """
        for name, value in tree.items():
            if isinstance(value, dict):
                subdirectory = directory / name
                subdirectory.mkdir()

                assert subdirectory.exists()

                self._build(subdirectory, value)
            else:
                file = directory / name
                if value:
                    file.touch(mode=value)
                else:
                    file.touch()

                assert file.exists()

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
