import argparse
import os
import platform
import random
import re
import textwrap

import numpy as np
import vidtoolz
from moviepy import (
    AudioFileClip,
    ColorClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    vfx,
)
from PIL import Image, ImageDraw, ImageFont


def create_gradient_clip(size, colors, duration):
    """
    Create a video clip with a linear gradient background.
    """
    width, height = size
    gradient = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        interp_factor = y / (height - 1)
        color_index = int(interp_factor * (len(colors) - 1))
        local_interp = (interp_factor * (len(colors) - 1)) - color_index

        c1 = np.array(colors[color_index])
        c2 = np.array(colors[min(color_index + 1, len(colors) - 1)])

        color = c1 * (1 - local_interp) + c2 * local_interp
        gradient[y, :, :] = color.astype(np.uint8)

    return ImageClip(gradient).with_duration(duration)


def get_audio_clip(duration, audio_volume):
    audio_path = os.path.join(os.path.dirname(__file__), "assets", "charkha.mp3")
    audio_clip = AudioFileClip(audio_path).subclipped(0, duration)
    audio_clip = audio_clip.with_volume_scaled(audio_volume)
    return audio_clip


def get_effect_clip():
    """
    Load the Sharpwipereverb sound effect.
    """
    effect_path = os.path.join(
        os.path.dirname(__file__), "assets", "Sharpwipereverb.m4a"
    )
    return AudioFileClip(effect_path)


def generate_output_filename(text, output=None):
    """
    Generate an output filename from the text if none is provided.

    Args:
        text (str): The input text to use in the filename.
        output (str or None): The user-provided output filename, if any.

    Returns:
        str: A valid output filename.
    """
    if output:
        return output

    # Remove any characters not safe for filenames
    safe_text = re.sub(r"[^\w\s-]", "", text)
    filename = safe_text.strip().replace(" ", "-")
    return f"{filename}.mp4"


def create_text_colorclip(
    text,
    size=(1920, 1080),
    color=(0, 0, 0),
    gradient_colors=None,
    text_color="white",
    font="Arial",
    fontsize=50,
    fade_duration=1.0,
    duration=5.0,
    audio_volume=0.01,
    padding=30,
    expand=False,
    effect=False,
    glitch=False,
    fps=60,
):
    """
    Create a color clip with overlaid text, both fading in and out.
    """

    def scale_by_frame(get_frame, t):
        total_frames = duration * fps
        frame = int(round(t * fps))
        progress = min(frame / total_frames, 1.0)
        scale = 1.0 + 0.1 * progress
        return scale

    if gradient_colors:
        bg_clip = create_gradient_clip(size, gradient_colors, duration)
    else:
        bg_clip = ColorClip(size, color=color, duration=duration)

    bg_clip = bg_clip.with_effects(
        [vfx.FadeIn(fade_duration), vfx.FadeOut(fade_duration)]
    )

    # Calculate available width for text after accounting for padding
    available_width = size[0] - 2 * padding

    # Wrap text based on actual pixel width using PIL
    try:
        pil_font = ImageFont.truetype(font, fontsize)
    except OSError:
        pil_font = ImageFont.load_default()

    temp_image = Image.new("RGB", (size[0], 1000))
    temp_draw = ImageDraw.Draw(temp_image)
    wrapped_lines = wrap_text_to_width(text, pil_font, temp_draw, available_width)
    wrapped_text = "\n".join(wrapped_lines)

    text_clip = (
        TextClip(
            text=wrapped_text,
            font_size=fontsize,
            font=font,
            color=text_color,
            margin=(padding, padding),
            method="caption",
            size=size,
        )
        .with_duration(duration)
        .with_effects([vfx.FadeIn(fade_duration), vfx.FadeOut(fade_duration)])
        .with_position("center")
    )

    # Apply expanding effect if enabled
    if expand:
        # Slowly scale text from 90% to 110% of original size
        text_clip = text_clip.resized(
            # lambda t: 1.0 + 0.1 * (round(t * fps) / (duration * fps))
            lambda t: scale_by_frame(None, t)
        )

    bg_clip = bg_clip.with_fps(fps)
    text_clip = text_clip.with_fps(fps)
    final_clip = CompositeVideoClip([bg_clip, text_clip]).with_fps(fps)
    audio_clip = get_audio_clip(duration, audio_volume)
    audio_clip = audio_clip.with_fps(44100)

    # If effect is enabled, mix SFX at start
    if effect:
        effect_clip = get_effect_clip()
        effect_clip.with_fps(44100)
        # Combine both effect and background audio
        audio_clip = CompositeAudioClip([effect_clip, audio_clip])

    # Apply glitch effect if enabled
    if glitch:
        final_clip = apply_glitch_effect(final_clip, glitch_intensity=20, fps=fps)

    audio_clip = audio_clip.with_fps(44100)
    final_clip = final_clip.with_audio(audio_clip)

    return final_clip


def apply_glitch_effect(clip, glitch_intensity=20, fps=60):
    """
    Apply a glitch effect to a video clip.
    Creates random horizontal slices with displacement and color shifts.

    Args:
        clip: The video clip to apply the effect to.
        glitch_intensity (int): Maximum pixel displacement for glitch effect.
        fps (int): Frames per second of the video.

    Returns:
        The clip with glitch effect applied.
    """
    def glitch_frame(get_frame, t):
        frame = get_frame(t)
        height, width = frame.shape[:2]

        # Apply glitch randomly (about 30% of frames)
        if random.random() > 0.3:
            return frame

        # Create a copy of the frame
        glitched = frame.copy()

        # Number of horizontal slices
        num_slices = random.randint(3, 8)

        for _ in range(num_slices):
            # Random slice height and position
            slice_height = random.randint(5, height // 10)
            y_start = random.randint(0, height - slice_height)
            y_end = y_start + slice_height

            # Random horizontal displacement
            displacement = random.randint(-glitch_intensity, glitch_intensity)

            # Get the slice
            slice_data = glitched[y_start:y_end, :].copy()

            # Apply displacement with wrap-around
            if displacement > 0:
                glitched[y_start:y_end, displacement:] = slice_data[:, :width - displacement]
                glitched[y_start:y_end, :displacement] = slice_data[:, -displacement:]
            elif displacement < 0:
                displacement = abs(displacement)
                glitched[y_start:y_end, :-displacement] = slice_data[:, displacement:]
                glitched[y_start:y_end, -displacement:] = slice_data[:, :displacement]

        # Add occasional color channel shift (RGB split effect)
        if random.random() > 0.5:
            channel_shift = random.randint(1, 5)
            if random.random() > 0.5:
                # Shift red channel
                glitched[:, :, 0] = np.roll(glitched[:, :, 0], channel_shift, axis=1)
            else:
                # Shift blue channel
                glitched[:, :, 2] = np.roll(glitched[:, :, 2], -channel_shift, axis=1)

        return glitched

    return clip.transform(glitch_frame)


def wrap_text_to_width(text, font, draw, max_width):
    """
    Wrap text into multiple lines so that each line fits within max_width.

    Args:
        text (str): The text to wrap.
        font: PIL ImageFont object.
        draw: PIL ImageDraw object.
        max_width (int): Maximum width in pixels for each line.

    Returns:
        list: List of wrapped lines.
    """
    lines = []
    words = text.split()

    if not words:
        return lines

    current_line = words[0]

    for word in words[1:]:
        test_line = current_line + " " + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = bbox[2] - bbox[0]

        if test_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)
    return lines


def get_fitting_fontsize_multiline(
    text, font_path, max_width, padding=0, max_fontsize=300, min_fontsize=10
):
    """
    Determine the largest font size such that the multiline text fits within max_width.
    """
    # Fixed margin for text wrapping (20 pixels on each side)
    wrap_margin = 20

    for fontsize in range(max_fontsize, min_fontsize, -1):
        try:
            font = ImageFont.truetype(font_path, fontsize)
        except OSError:
            font = ImageFont.load_default()

        # Create dummy image to measure text
        image = Image.new("RGB", (max_width, 1000))
        draw = ImageDraw.Draw(image)

        # Calculate available width for text wrapping after accounting for wrap margin
        available_width = max_width - 2 * wrap_margin

        # Wrap text based on actual pixel width
        wrapped_lines = wrap_text_to_width(text, font, draw, available_width)

        # Measure the maximum line width
        max_line_width = 0
        for line in wrapped_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            max_line_width = max(max_line_width, line_width)

        if max_line_width + 2 * padding <= max_width:
            return fontsize
    return min_fontsize


def parse_color(color_str):
    """
    Convert color string like "255,0,0" to RGB tuple.
    """
    try:
        return tuple(map(int, color_str.split(",")))
    except:
        raise argparse.ArgumentTypeError("Color must be in R,G,B format (e.g. 255,0,0)")


def parse_gradient_colors(color_str):
    """
    Convert a string of semicolon-separated RGB colors to a list of tuples.
    e.g., "255,0,0;0,255,0" -> [(255,0,0), (0,255,0)]
    """
    try:
        colors = []
        for c in color_str.split(";"):
            rgb = tuple(map(int, c.split(" ")))
            if len(rgb) != 3:
                raise ValueError
            colors.append(rgb)
        return colors
    except:
        raise argparse.ArgumentTypeError(
            "Gradient colors must be in R,G,B;R,G,B format (e.g. 255,0,0;0,255,0)"
        )


def create_parser(subparser):
    parser = subparser.add_parser(
        "textclip", description="Create a color clip with overlaid text"
    )
    # Add subprser arguments here.
    default_font = "Papyrus" if platform.system() == "Darwin" else "Arial"
    parser.add_argument("text", type=str, help="Text to display.")
    parser.add_argument(
        "-f",
        "--font",
        type=str,
        default=default_font,
        help="Font name to use. Ex Noteworthy, Melno, Papyrus, Zapfino (default: %(default)s)",
    )
    parser.add_argument(
        "-fs",
        "--fontsize",
        type=int,
        default=210,
        help="Font size. (default: %(default)s)",
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=float,
        default=3.0,
        help="Duration of video in seconds. (default: %(default)s)",
    )
    parser.add_argument(
        "-fd",
        "--fade-duration",
        type=float,
        default=0.5,
        help="Fade-in/out duration. (default: %(default)s)",
    )
    parser.add_argument(
        "-tc",
        "--text-color",
        type=str,
        default="white",
        help="Text color. (default: %(default)s)",
    )
    parser.add_argument(
        "-bg",
        "--bg-color",
        type=parse_color,
        default=(0, 0, 0),
        help="Background color as R,G,B. (default: %(default)s)",
    )
    parser.add_argument(
        "-gc",
        "--gradient-colors",
        type=parse_gradient_colors,
        default=None,
        help="Semicolon-separated list of R,G,B colors for the gradient background. e.g. 255,0,0;0,0,255",
    )
    parser.add_argument(
        "-s",
        "--size",
        type=str,
        default="1920,1080",
        help="Video size as width,height. (default: %(default)s)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output video file name. (default: %(default)s)",
    )
    parser.add_argument(
        "--fps", type=int, default=60, help="Frames per second. (default: %(default)s)"
    )

    parser.add_argument(
        "-p",
        "--padding",
        type=int,
        default=30,
        help="Padding on text (default: %(default)s)",
    )

    parser.add_argument(
        "-e",
        "--expand",
        action="store_true",
        help="If set, the text will slowly enlarge during the video.",
    )

    parser.add_argument(
        "-ef",
        "--effect",
        action="store_true",
        help="If set, adds Sharpwipereverb sound effect at the start.",
    )

    parser.add_argument(
        "-g",
        "--glitch",
        action="store_true",
        help="If set, adds a glitch effect to the text.",
    )
    return parser


class ViztoolzPlugin:
    """Create a color clip with overlaid text"""

    __name__ = "textclip"

    @vidtoolz.hookimpl
    def register_commands(self, subparser):
        self.parser = create_parser(subparser)
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        width, height = map(int, args.size.split(","))
        output = generate_output_filename(args.text, args.output)

        fontsize = get_fitting_fontsize_multiline(
            text=args.text,
            font_path=args.font,
            max_width=width,
            padding=args.padding,
            max_fontsize=args.fontsize,  # start from user's preferred size
        )

        clip = create_text_colorclip(
            text=args.text,
            size=(width, height),
            color=args.bg_color,
            gradient_colors=args.gradient_colors,
            text_color=args.text_color,
            font=args.font,
            fontsize=fontsize,
            fade_duration=args.fade_duration,
            duration=args.duration,
            padding=args.padding,
            expand=args.expand,
            effect=args.effect,
            glitch=args.glitch,
            fps=args.fps,
        )

        clip.write_videofile(
            output,
            fps=args.fps,
            audio_codec="aac",
            codec="libx264",
            ffmpeg_params=["-pix_fmt", "yuv420p"],
        )

    def hello(self, args):
        # this routine will be called when "vidtoolz "textclip is called."
        print("Hello! This is an example ``vidtoolz`` plugin.")


textclip_plugin = ViztoolzPlugin()
