# vidtoolz-colored-textclip

[![PyPI](https://img.shields.io/pypi/v/vidtoolz-colored-textclip.svg)](https://pypi.org/project/vidtoolz-colored-textclip/)
[![Changelog](https://img.shields.io/github/v/release/sukhbinder/vidtoolz-colored-textclip?include_prereleases&label=changelog)](https://github.com/sukhbinder/vidtoolz-colored-textclip/releases)
[![Tests](https://github.com/sukhbinder/vidtoolz-colored-textclip/workflows/Test/badge.svg)](https://github.com/sukhbinder/vidtoolz-colored-textclip/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/vidtoolz-colored-textclip/blob/main/LICENSE)

Create a color clip with overlaid text

## Installation

First install [vidtoolz](https://github.com/sukhbinder/vidtoolz).

```bash
pip install vidtoolz
```

Then install this plugin in the same environment as your vidtoolz application.

```bash
vidtoolz install vidtoolz-colored-textclip
```
## Usage

type ``vid textclip --help`` to get help



## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd vidtoolz-colored-textclip
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
