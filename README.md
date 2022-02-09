# fideslib

[![Latest Version][pypi-image]][pypi-url]
[![License][license-image]][license-url]
[![Code style: black][black-image]][black-url]
[![Checked with mypy][mypy-image]][mypy-url]
[![Twitter][twitter-image]][twitter-url]

Each top-level directory in this repository (except `tests/`) represents a discrete package that exposes specific functionality intended to be shared across multiple fides tool codebases. Any amount of packages may be independently consumed by a given fides tool.

## Installation

1. Add `fideslib` to the `requirements.txt` (or equivalent) file:

    ```
    fideslib==1.0.0
    ```

    Alternatively, include specific packages by specifying them by name:

    ```
    fideslib[cryptography,oauth]==1.0.0
    ```

1. Within the project's virtual environment, install the required dependencies with the `pip install` command:

    ```sh
    pip install -r requirements.txt
    ```

> Install `fideslib` globally by running the `pip install` command outside of any virtual environment:
>
> ```
> pip install fideslib
> ```

## Usage

The packages exposed by this repository are self-contained and unrelated to one another. Thus, usage varies from package to package. For package-specific usage guides, see the `README.md` files located within each package's dedicated directory:

- [Cryptography](./cryptography) ([README](./cryptography/README.md))
- [OAuth](./oauth) ([README](./oauth/README.md))

## Contributing

We welcome and encourage all types of contributions and improvements!

Read about the [Fides community](https://ethyca.github.io/fides/community/hints_tips/) or dive into the [development guides](https://ethyca.github.io/fides/development/overview) for information about contributions, documentation, code style, testing, and more. Ethyca is committed to fostering a safe and collaborative environment, such that all interactions are governed by the [Fides Code of Conduct](https://ethyca.github.io/fides/community/code_of_conduct/).

## License

The Fides ecosystem of tools are licensed under the [Apache Software License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
Fides tools are built on [Fideslang](https://github.com/ethyca/privacy-taxonomy), the Fides language specification, which is licensed under [CC by 4](https://github.com/ethyca/privacy-taxonomy/blob/main/LICENSE).

Fides is created and sponsored by [Ethyca](https://ethyca.com/): a developer tools company building the trust infrastructure of the internet. If you have questions or need assistance getting started, let us know at fides@ethyca.com!

[pypi-image]: https://img.shields.io/pypi/v/fideslib.svg
[pypi-url]: https://pypi.python.org/pypi/fideslib/
[license-image]: https://img.shields.io/:license-Apache%202-blue.svg
[license-url]: https://www.apache.org/licenses/LICENSE-2.0.txt
[black-image]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-url]: https://github.com/psf/black/
[mypy-image]: http://www.mypy-lang.org/static/mypy_badge.svg
[mypy-url]: http://mypy-lang.org/
[twitter-image]: https://img.shields.io/twitter/follow/ethyca?style=social
[twitter-url]: https://twitter.com/ethyca
