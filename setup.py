# pylint: disable=missing-function-docstring

from pathlib import Path
from setuptools import setup, find_packages

# Packages
CRYPTO = "cryptography"
OAUTH = "oauth"


def parse_local_file(filename: str) -> str:
    here = Path(__file__).parent.resolve()
    return (here / filename).read_text("utf-8").strip()


def list_requirements(filename: str) -> list[str]:
    return parse_local_file(filename).split("\n")


setup(
    name="fideslib",
    version="0.0.1",
    description="Shared libraries, for use in any fides project.",
    long_description=parse_local_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/ethyca/fideslib",
    author="Ethyca, Inc.",
    author_email="fidesteam@ethyca.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries",
    ],
    package_dir={
        CRYPTO: CRYPTO,
        OAUTH: OAUTH,
    },
    packages=find_packages(where="."),
    python_requires=">=3.9, <4",
    extras_require={
        "dev": list_requirements("dev-requirements.txt"),
        CRYPTO: list_requirements(f"{CRYPTO}/requirements.txt"),
        OAUTH: list_requirements(f"{OAUTH}/requirements.txt"),
    },
)