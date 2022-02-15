from pathlib import Path
from setuptools import setup, find_packages
from typing import List


def read_requirements(filename: str) -> List[str]:
    with open(filename, "r") as file:
        requirements = file.read().strip().split("\n")
    return requirements


# Requirements and Dependencies
dev_requires = read_requirements("dev-requirements.txt")
cryptography_requires = read_requirements("fideslib/cryptography/requirements.txt")
oauth_requires = read_requirements("fideslib/oauth/requirements.txt")

extras = {"crypto": cryptography_requires, "oauth": oauth_requires}
extras["all"] = sum([value for key, value in extras.items()], [])

setup(
    name="fideslib",
    version="0.0.1",
    description="Shared libraries, for use in any fides project.",
    long_description=open("README.md").read(),
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
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries",
    ],
    package_dir={"": "fideslib"},
    python_requires=">=3.8, <4",
    dev_requires=dev_requires,
    extras_require=extras,
)
