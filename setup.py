from typing import List

from setuptools import setup


def read_requirements(filename: str) -> List[str]:
    """
    Returns the contents of a requirements file, as a list.
    """

    with open(filename, "r") as file:
        requirements = file.read().strip().split("\n")
    return requirements


# Requirements and Dependencies
dev_requires = read_requirements("dev-requirements.txt")
cryptography_requires = read_requirements("fideslib/cryptography/requirements.txt")
oauth_requires = read_requirements("fideslib/oauth/requirements.txt")

extras = {
    "cryptography": cryptography_requires,
    "oauth": oauth_requires,
}
extras["all"] = sum([value for _, value in extras.items()], [])

setup(
    name="fideslib",
    version="1.0.2",
    description="Shared libraries, for use in any fides project.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ethyca/fideslib",
    author="Ethyca, Inc.",
    author_email="fidesteam@ethyca.com",
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
    ],
    package_dir={"": "fideslib"},
    python_requires=">=3.8, <4",
    dev_requires=dev_requires,
    extras_require=extras,
)
