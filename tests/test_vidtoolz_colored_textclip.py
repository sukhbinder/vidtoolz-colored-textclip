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
    assert result.content is None
    assert result.duration == 3.0
    assert result.font == default_font
    assert result.fontsize == 150
    assert result.text_color == "white"
    assert result.fade_duration == 0.5
    assert result.bg_color == (0, 0, 0)
    assert result.size == "1920,1080"
    assert result.output is None
    assert result.fps == 60
    assert result.expand is False
    assert result.effect is False
    assert result.glitch is False
    assert result.random_gradient is False


def test_glitch_argument():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    result = parser.parse_args(["hello", "-g"])
    assert result.glitch is True

    result = parser.parse_args(["hello", "--glitch"])
    assert result.glitch is True


def test_random_gradient_argument():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    assert parser.parse_args(["hello", "-rg"]).random_gradient is True
    assert parser.parse_args(["hello", "--random-gradient"]).random_gradient is True


def test_content_argument():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    result = parser.parse_args(["Main title", "--content", "Supporting text"])
    assert result.content == "Supporting text"


def test_longer_content_moves_title_up():
    font = str(Path(__file__).parent / "Keyboard.ttf")
    short_layout = w.calculate_content_layout(
        "Main title", "Short support", (1920, 1080), font, 120, 20
    )
    long_layout = w.calculate_content_layout(
        "Main title",
        "Supporting details " * 80,
        (1920, 1080),
        font,
        120,
        20,
    )

    assert long_layout["content_height"] > short_layout["content_height"]
    assert long_layout["top"] < short_layout["top"]


def test_generate_random_gradient_colors():
    colors = w.generate_random_gradient_colors()

    assert 2 <= len(colors) <= 4
    assert all(len(color) == 3 for color in colors)
    assert all(0 <= channel <= 255 for color in colors for channel in color)


def test_resolve_gradient_colors_prefers_explicit_colors(monkeypatch):
    explicit_colors = [(255, 0, 0), (0, 0, 255)]
    monkeypatch.setattr(
        w,
        "generate_random_gradient_colors",
        lambda: pytest.fail("random colors should not replace explicit colors"),
    )

    assert (
        w.resolve_gradient_colors(explicit_colors, random_gradient=True)
        == explicit_colors
    )


def test_resolve_gradient_colors_generates_random_palette(monkeypatch):
    generated_colors = [(1, 2, 3), (4, 5, 6)]
    monkeypatch.setattr(w, "generate_random_gradient_colors", lambda: generated_colors)

    assert w.resolve_gradient_colors(random_gradient=True) == generated_colors
    assert w.resolve_gradient_colors() is None

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
