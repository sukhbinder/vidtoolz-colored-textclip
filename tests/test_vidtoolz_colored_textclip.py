import pytest
import vidtoolz_colored_textclip as w

from unittest import mock

from argparse import ArgumentParser
import platform


def test_create_parser():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    assert parser is not None
    default_font = "Papyrus" if platform.system() == "Darwin" else "Arial"

    result = parser.parse_args(["hello"])
    assert result.text == "hello"
    assert result.duration == 4.0
    assert result.font == default_font
    assert result.fontsize == 100
    assert result.text_color == "white"
    assert result.fade_duration == 1.0
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
    assert w.parse_gradient_colors("255,0,0;0,255,0") == [(255, 0, 0), (0, 255, 0)]


def test_parse_gradient_colors_invalid():
    with pytest.raises(Exception):
        w.parse_gradient_colors("255,0,0;0,255")


# ---------- Tests for create_text_colorclip ----------


@mock.patch("vidtoolz_colored_textclip.AudioFileClip")
@mock.patch("vidtoolz_colored_textclip.CompositeVideoClip")
@mock.patch("vidtoolz_colored_textclip.TextClip")
@mock.patch("vidtoolz_colored_textclip.ColorClip")
def test_create_text_colorclip_mocks_called(
    ColorClipMock, TextClipMock, CompositeVideoClipMock, AudioFileClipMock
):
    mock_bg_clip = mock.Mock()
    mock_text_clip = mock.Mock()
    mock_final_clip = mock.Mock()
    mock_audio_clip = mock.Mock()

    # Setup return values
    ColorClipMock.return_value.with_effects.return_value = mock_bg_clip
    TextClipMock.return_value.with_duration.return_value.with_effects.return_value.with_position.return_value = (
        mock_text_clip
    )
    CompositeVideoClipMock.return_value = mock_final_clip
    AudioFileClipMock.return_value.subclipped.return_value.with_volume_scaled.return_value = (
        mock_audio_clip
    )
    mock_final_clip.with_audio.return_value = "final_video_clip_with_audio"

    text = "Test Clip"
    result = w.create_text_colorclip(text)

    assert result == "final_video_clip_with_audio"
    ColorClipMock.assert_called_once()
    TextClipMock.assert_called_once_with(
        text=text,
        font_size=50,
        font="Arial",
        color="white",
        margin=(30, 30),
        method="caption",
        size=(1920, 1080),
    )
    CompositeVideoClipMock.assert_called_once_with([mock_bg_clip, mock_text_clip])
    AudioFileClipMock.assert_called_once()
    mock_final_clip.with_audio.assert_called_once_with(mock_audio_clip)


@mock.patch("vidtoolz_colored_textclip.create_gradient_clip")
@mock.patch("vidtoolz_colored_textclip.AudioFileClip")
@mock.patch("vidtoolz_colored_textclip.CompositeVideoClip")
@mock.patch("vidtoolz_colored_textclip.TextClip")
@mock.patch("vidtoolz_colored_textclip.ColorClip")
def test_create_text_colorclip_with_gradient(
    ColorClipMock,
    TextClipMock,
    CompositeVideoClipMock,
    AudioFileClipMock,
    create_gradient_clip_mock,
):
    mock_bg_clip = mock.Mock()
    mock_text_clip = mock.Mock()
    mock_final_clip = mock.Mock()
    mock_audio_clip = mock.Mock()

    # Setup return values
    create_gradient_clip_mock.return_value.with_effects.return_value = mock_bg_clip
    TextClipMock.return_value.with_duration.return_value.with_effects.return_value.with_position.return_value = (
        mock_text_clip
    )
    CompositeVideoClipMock.return_value = mock_final_clip
    AudioFileClipMock.return_value.subclipped.return_value.with_volume_scaled.return_value = (
        mock_audio_clip
    )
    mock_final_clip.with_audio.return_value = "final_video_clip_with_audio"

    text = "Test Clip"
    gradient_colors = [(255, 0, 0), (0, 0, 255)]
    result = w.create_text_colorclip(text, gradient_colors=gradient_colors)

    assert result == "final_video_clip_with_audio"
    create_gradient_clip_mock.assert_called_once_with(
        (1920, 1080), gradient_colors, 5.0
    )
    ColorClipMock.assert_not_called()
    TextClipMock.assert_called_once_with(
        text=text,
        font_size=50,
        font="Arial",
        color="white",
        margin=(30, 30),
        method="caption",
        size=(1920, 1080),
    )
    CompositeVideoClipMock.assert_called_once_with([mock_bg_clip, mock_text_clip])
    AudioFileClipMock.assert_called_once()
    mock_final_clip.with_audio.assert_called_once_with(mock_audio_clip)
