"""Usefull tasks to `invoke` when developing."""

from pathlib import Path

import pdoc
from invoke import task

import temptree

DIR = Path(__file__).parent
DOCS_DIR = DIR / "docs"
DOCS_TARGET = DOCS_DIR / "index.html"
NOJEKYLL_TARGET = DOCS_DIR / ".nojekyll"
README_TARGET = DIR / "README.md"


def get_module_doc():
    """Gives the module documentation object."""
    context = pdoc.Context()
    module = pdoc.Module(temptree, context=context)
    pdoc.link_inheritance(context=context)

    return module


@task
def doc(c):
    """Generates the documentation"""
    module = get_module_doc()

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    NOJEKYLL_TARGET.touch()
    DOCS_TARGET.touch()
    DOCS_TARGET.write_text(module.html())


@task
def readme(c):
    """Generates the readme"""
    module = get_module_doc()

    README_TARGET.touch()
    README_TARGET.write_text("\n".join(["temptree", "========", module.docstring]))
