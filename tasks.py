"""Development tasks."""

from pathlib import Path

import pdoc
from invoke import task

import temptree


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
    docs = Path(__file__).parent / "docs"
    target = docs / "index.html"
    nojekyll = docs / ".nojekyll"
    module = get_module_doc()

    docs.mkdir(parents=True, exist_ok=True)
    nojekyll.touch()
    target.touch()
    target.write_text(module.html())


@task
def readme(c):
    """Generates the readme"""
    target = Path(__file__).parent / "README.md"
    module = get_module_doc()

    target.touch()
    target.write_text("\n".join(["temptree", "========", module.docstring]))


@task(lint, quick_test, doc, readme, name="pre-commit")
def pre_commit(c):
    """Run tasks required for commiting"""
