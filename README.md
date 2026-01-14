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


```
usage: vid textclip [-h] [-f FONT] [-fs FONTSIZE] [-d DURATION]
                    [-fd FADE_DURATION] [-tc TEXT_COLOR] [-bg BG_COLOR]
                    [-gc GRADIENT_COLORS] [-s SIZE] [-o OUTPUT] [--fps FPS]
                    [-p PADDING]
                    text

Create a color clip with overlaid text

positional arguments:
  text                  Text to display.

optional arguments:
  -h, --help            show this help message and exit
  -f FONT, --font FONT  Font name to use. Ex Noteworthy, Melno, Papyrus,
                        Zapfino (default: Arial)
  -fs FONTSIZE, --fontsize FONTSIZE
                        Font size. (default: 80)
  -d DURATION, --duration DURATION
                        Duration of video in seconds. (default: 5.0)
  -fd FADE_DURATION, --fade-duration FADE_DURATION
                        Fade-in/out duration. (default: 1.0)
  -tc TEXT_COLOR, --text-color TEXT_COLOR
                        Text color. (default: white)
  -bg BG_COLOR, --bg-color BG_COLOR
                        Background color as R,G,B. (default: (0, 0, 0))
  -gc GRADIENT_COLORS, --gradient-colors GRADIENT_COLORS
                        Semicolon-separated list of R,G,B colors for the
                        gradient background. e.g. 255,0,0;0,0,255
  -s SIZE, --size SIZE  Video size as width,height. (default: 1920,1080)
  -o OUTPUT, --output OUTPUT
                        Output video file name. (default: None)
  --fps FPS             Frames per second. (default: 60)
  -p PADDING, --padding PADDING
                        Padding on text (default: 30)

```

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
