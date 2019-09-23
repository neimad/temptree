temptree
========
Generates temporary files and directories from a tree.

[![Build Status][ci-badge]][ci]
[![PyPI][pypi-badge]][package]
[![Python Version][py-versions-badge]][package]
[![License][license-badge]][license]

The provided `TemporaryTree` class allows to create complete files hierarchies under a
root `tempfile.TemporaryDirectory`.

It is well suited for usage within *doctests* :

    >>> from temptree import TemporaryTree

    >>> with TemporaryTree(["foo.py", "bar.py"]) as root:
    ...     (root / "foo.py").is_file()
    ...     (root / "bar.py").is_file()
    ...
    True
    True

A complete file hierarchy can be easily created, including text files content and files
mode:

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

[The complete documentation][documentation] is available from Github Pages.

Development
-----------

The development tasks are managed using [Invoke]. Use it to list the available tasks:

    inv -l

Use the `pre-commit` task within your repository `pre-commit` hook:

    poetry run invoke pre-commit

Contributing
------------

This project is hosted on [Github][repository].

If you're facing an issue using `temptree`, please look at
[the existing tickets][issues]. Then you may open a new one.

You may also make a [push request][pull-requests] to help improve it.

License
-------

`temptree` is licensed under the [GNU GPL 3][GPL] or later.

[ci]: https://travis-ci.org/neimad/temptree
[package]: https://pypi.org/project/temptree/
[ci-badge]: https://img.shields.io/travis/neimad/temptree?style=flat-square
[py-versions-badge]: https://img.shields.io/pypi/pyversions/temptree?style=flat-square
[pypi-badge]: https://img.shields.io/pypi/v/temptree?style=flat-square
[license]: https://github.com/neimad/temptree/blob/master/LICENSE.md
[license-badge]: https://img.shields.io/github/license/neimad/temptree?style=flat-square
[documentation]: https://neimad.github.io/temptree/
[Invoke]: https://www.pyinvoke.org/
[repository]: https://github.com/neimad/temptree
[issues]: https://github.com/neimad/temptree/issues
[pull-requests]: https://github.com/neimad/temptree/pulls
[GPL]: https://www.gnu.org/licenses/gpl.html