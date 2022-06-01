# fideslib

[![Latest Version][pypi-image]][pypi-url]
[![License][license-image]][license-url]
[![Code style: black][black-image]][black-url]
[![Checked with mypy][mypy-image]][mypy-url]
[![Twitter][twitter-image]][twitter-url]

## Installation

```console
pip install fideslib
```


## Usage

### Config

Examples here will assume a project structure of `src/my_project` where `my_project` is
the root module.

To use the default config settings create a module and file to store the config. In
this example we will use `src/my_project/core/config.py`.


```py
from fideslib.core.config import get_config

config = get_config()
```

Then the config can be used in other files by importing `config`.

```py
from my_project.core.config import config
```

The default config can be overridden by extending the settings classes. With the same
setup as above, in the `src/my_project/core/config.py` file:

```py
from fideslib.core.config import DatabaseSettings, FidesSettings, get_config


class ExtendedDataBaseSettings(DatabaseSettings):
    extra_field: str

    class Config:
        env_prefix = "FIDESOPS__DATABASE__"


class ExtendedFidesSettings(FidesSettings):
    database: ExtendedDataBaseSettings


config = get_config(ExtendedDataBaseSettings)  # pass the name of the custom settings class here
```

Now the resulting `config.database` will contain the extra `extra_field` field and
`ExtendedDataBaseSettings` will look for environment variables with
`FIDESOBS__DATABASE__`.

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
