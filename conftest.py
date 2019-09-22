"""Pytest initialization."""

from os import getenv

from hypothesis import settings

settings.register_profile(
    "default", max_examples=getenv("HYPOTHESIS_MAX_EXAMPLES", 100)
)

settings.load_profile("default")
