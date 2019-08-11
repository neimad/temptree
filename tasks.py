"""Development tasks."""

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
def lint(c):
    """Lint the source code"""
    c.run("flake8", hide="out")
    c.run("doc8", hide="out")


@task(name="quick-test")
def quick_test(c):
    """Run quick tests"""
    c.run("pytest", hide="out")


@task()
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


@task(lint, quick_test, doc, readme, name="pre-commit")
def pre_commit(c):
    """Run tasks required for commiting"""
    c.run(f"git add {DOCS_TARGET}")
    c.run(f"git add {NOJEKYLL_TARGET}")
    c.run(f"git add {README_TARGET}")
