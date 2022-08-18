#!/usr/bin/env python
from setuptools import find_packages, setup

project = "flake8-logging-format"
version = "0.7.5"
long_description = open("README.md").read()

setup(
    name=project,
    version=version,
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/flake8-logging-format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    keywords="microcosm",
    install_requires=[
    ],
    extras_require={
        "test": [
            "pytest",
            "pytest-cov",
            "PyHamcrest",
        ],
        "lint": [
            "flake8",
        ]
    },
    dependency_links=[
    ],
    entry_points={
        "flake8.extension": [
            "G = logging_format.api:LoggingFormatValidator",
        ],
        "logging.extra.example": [
            "example = logging_format.whitelist:example_whitelist",
        ],
    },
    classifiers=[
        "Framework :: Flake8",
    ],
)
