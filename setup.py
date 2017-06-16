#!/usr/bin/env python
from setuptools import find_packages, setup

project = "flake8-logging-format"
version = "0.2.0"

setup(
    name=project,
    version=version,
    description="Flake8 extension to validate (lack of) logging format strings",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/flake8-logging-format",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    keywords="microcosm",
    install_requires=[
    ],
    setup_requires=[
        "nose>=1.3.6",
    ],
    dependency_links=[
    ],
    entry_points={
        "flake8.extension": [
            "logging-format = logging_format.api:LoggingFormatValidator",
        ],
        "logging.extra.example": [
            "example = logging_format.whitelist:example_whitelist",
        ],
    },
    tests_require=[
        "coverage>=3.7.1",
        "PyHamcrest>=1.8.5",
    ],
)
