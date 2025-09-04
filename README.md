[![Testing](https://github.com/AresSC2/cython-extensions-sc2/actions/workflows/test.yml/badge.svg)](https://github.com/AresSC2/cython-extensions-sc2/actions/workflows/test.yml)
[![Deploy Documentation](https://github.com/AresSC2/cython-extensions-sc2/actions/workflows/pages.yml/badge.svg)](https://github.com/AresSC2/cython-extensions-sc2/actions/workflows/pages.yml)
<br>

# cython-extensions-sc2

[API Documentation](https://aressc2.github.io/cython-extensions-sc2/) - for a full list of included functions.

`cython-extensions-sc2` is a library designed for the [python-sc2](https://github.com/BurnySc2/python-sc2) API. 
Its purpose is to offer optimized Cython alternatives for commonly used functions, 
along with additional useful custom functions.

<b>Note: This library is included for `ares-sc2` users by default, no further setup is required.</b>

This library also supports `python-sc2` and `sharpy-sc2` bots, see Getting Started below.

Example speedups, results may vary depending on machine and exact scenario.
This is by no means a list of all functionality offered.

| python-sc2 function           | cython speedup                           |
|-------------------------------|------------------------------------------|
| `units.closest_to`            | 6.85 - 13x speedup depending on scenario |
| `distance_to`                 | 3 to 7x speedup depending on scenario    |
| `position.center`             | 2x speedup                               |
| `already_pending` for units   | 6.62x speedup                            |
| `units.in_attack_range`       | 2.05x speedup                            |
| `units.sorted_by_distance_to` | 8.62x speedup                            |
| `unit.is_facing`              | 9.1x speedup                             |
| `Point2.towards`              | 14.29x speedup                           |
| `has_creep`                   | 4 - 5x speedup                           |
| `in_pathing_grid`             | 4 - 5x speedup                           |


Tip: use `cy_distance_to_squared` where possible for extra 1.3x speedup.

## Getting started

To quickly get up and running locally (for python versions 3.10, 3.11, 3.12, 3.13), install `cython-extensions-sc2` with:

`pip install cython-extensions-sc2`

### Shipping to ladder
When shipping to [ladder](https://aiarena.net/), grab `ubuntu-latest_python3.12.zip` from releases in this repo
and extract `cython_extensions` directory within the zip to the root of your bot's directory, like so:

```
MyBot
└───cython_extensions
│   └───cython-extensions library files
└───your bot files and directories
```

### Alternative local setup
If you already have a `python-sc2`, or `sharpy-sc2` development environment setup,
then `cython-extensions` should work out the box with your bot without the need to install extra requirements. Simply check out the releases on this
repo and download the correct `zip` for your system.

![release](https://github.com/AresSC2/cython-extensions-sc2/assets/63355562/3c5084ee-5d61-4446-a0dc-4d0ce3421b34)

For example a Windows user should download `windows-latest_python3.1.zip`.

Inside this zip you will find a `cython_extensions` directory, this should be placed in your bot's root directory
like so:
```
MyBot
└───cython_extensions
│   └───cython-extensions library files
└───your bot files and directories
```

### Start using `cython-extensions-sc2`
For ease of use all cython functions are importable via the main module, for example:
```python
from cython_extensions import cy_distance_to, cy_attack_ready, cy_closest_to
```
note: in this project all library functions have a `cy_` prefix to prevent confusion with python alternatives.

### Contributor / Cloning the project
Install [poetry](https://python-poetry.org/) if you do not already have it installed.

Then to setup a full development environment run:
`poetry install --with dev,test,docs,semver`

This will set up a new environment, install all required dependencies and compile the cython code for your system.

If you modify the cython code, run `poetry build` to compile it.

#### Jupyter Notebooks
Run `poetry run jupyter notebook` to open jupyter notebook in the environment. See the notebooks 
directory for examples. Use `template_notebook.ipynb` as a starting point for your own notebooks.

#### Run Test Bot
Edit the map in `bot_test.py` and run with:
`poetry run python tests/bot_test.py`

#### Contributing
Contributors are very welcome! There are many missing alternative `python-sc2` functions, and if you're 
into optimization, the existing functions could likely be improved.

Please use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) if you choose to contribute, 
it helps the automatic releases detect
a new version and generates an accurate changelog.

Example git messages:

`feat: add new cython function`

`fix: fixed buggy function`

`test: add new test`

`ci: update github workflow`

`docs: add new docs`

`chore: add dependency`

