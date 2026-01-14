import platform
from argparse import ArgumentParser
from pathlib import Path

import pytest

import vidtoolz_colored_textclip as w


def test_create_parser():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    assert parser is not None
    default_font = "Papyrus" if platform.system() == "Darwin" else "Arial"

    result = parser.parse_args(["hello"])
    assert result.text == "hello"
    assert result.duration == 3.0
    assert result.font == default_font
    assert result.fontsize == 210
    assert result.text_color == "white"
    assert result.fade_duration == 0.5
    assert result.bg_color == (0, 0, 0)
    assert result.size == "1920,1080"
    assert result.output is None
    assert result.fps == 60


def test_plugin(capsys):
    w.textclip_plugin.hello(None)
    captured = capsys.readouterr()
    assert "Hello! This is an example ``vidtoolz`` plugin." in captured.out


def test_generate_output_filename_with_output():
    assert (
        w.generate_output_filename("Some Text", "custom_name.mp4") == "custom_name.mp4"
    )


def test_generate_output_filename_from_text_simple():
    assert w.generate_output_filename("Hello World") == "Hello-World.mp4"


def test_generate_output_filename_with_special_chars():
    text = "A title: with *weird* characters!"
    expected = "A-title-with-weird-characters.mp4"
    assert w.generate_output_filename(text) == expected


def test_generate_output_filename_with_leading_trailing_spaces():
    text = "  Clean this up  "
    expected = "Clean-this-up.mp4"
    assert w.generate_output_filename(text) == expected


def test_parse_gradient_colors_valid():
    assert w.parse_gradient_colors("255 0 0;0 255 0") == [(255, 0, 0), (0, 255, 0)]


def test_parse_gradient_colors_invalid():
    with pytest.raises(Exception):
        w.parse_gradient_colors("255,0,0;0,255")


def test_realcase(tmpdir):
    outfile = tmpdir / "test.mp4"
    fontpath = Path(__file__).parent / "Keyboard.ttf"
    argv = [
        "Sukhbinder Singh",
        "-e",
        "-ef",
        "-o",
        str(outfile),
        "-d",
        "2",
        "--fps",
        "10",
        "-f",
        str(fontpath),
    ]
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)
    args = parser.parse_args(argv)
    w.textclip_plugin.run(args)
    assert outfile.exists()
