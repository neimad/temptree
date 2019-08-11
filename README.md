temptree
========
Generates temporary files and directories from a tree.

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