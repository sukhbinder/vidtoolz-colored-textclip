import vidtoolz
import argparse
from moviepy import ColorClip, TextClip, CompositeVideoClip, vfx, AudioFileClip
import re
import os


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
    text_color="white",
    font="Arial",
    fontsize=50,
    fade_duration=1.0,
    duration=5.0,
    audio_volume=0.01,
):
    """
    Create a color clip with overlaid text, both fading in and out.
    """
    bg_clip = ColorClip(size, color=color, duration=duration).with_effects(
        [vfx.FadeIn(fade_duration), vfx.FadeOut(fade_duration)]
    )

    text_clip = (
        TextClip(text=text, font_size=fontsize, font=font, color=text_color)
        .with_duration(duration)
        .with_effects([vfx.FadeIn(fade_duration), vfx.FadeOut(fade_duration)])
        .with_position("center")
    )

    final_clip = CompositeVideoClip([bg_clip, text_clip])
    audio_path = os.path.join(os.path.dirname(__file__), "assets", "charkha.mp3")
    audio_clip = AudioFileClip(audio_path).subclipped(0, duration)
    audio_clip = audio_clip.with_volume_scaled(audio_volume)
    final_clip = final_clip.with_audio(audio_clip)

    return final_clip


def parse_color(color_str):
    """
    Convert color string like "255,0,0" to RGB tuple.
    """
    try:
        return tuple(map(int, color_str.split(",")))
    except:
        raise argparse.ArgumentTypeError("Color must be in R,G,B format (e.g. 255,0,0)")


def create_parser(subparser):
    parser = subparser.add_parser(
        "textclip", description="Create a color clip with overlaid text"
    )
    # Add subprser arguments here.
    parser.add_argument("text", type=str, help="Text to display.")
    parser.add_argument(
        "-f", "--font", type=str, default="Arial", help="Font name to use."
    )
    parser.add_argument("-fs", "--fontsize", type=int, default=80, help="Font size.")
    parser.add_argument(
        "-d",
        "--duration",
        type=float,
        default=5.0,
        help="Duration of video in seconds.",
    )
    parser.add_argument(
        "-fd", "--fade-duration", type=float, default=1.0, help="Fade-in/out duration."
    )
    parser.add_argument(
        "-tc", "--text-color", type=str, default="white", help="Text color."
    )
    parser.add_argument(
        "-bg",
        "--bg-color",
        type=parse_color,
        default=(0, 0, 0),
        help="Background color as R,G,B.",
    )
    parser.add_argument(
        "-s",
        "--size",
        type=str,
        default="1920,1080",
        help="Video size as width,height.",
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None, help="Output video file name."
    )
    parser.add_argument("--fps", type=int, default=60, help="Frames per second.")

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

        clip = create_text_colorclip(
            text=args.text,
            size=(width, height),
            color=args.bg_color,
            text_color=args.text_color,
            font=args.font,
            fontsize=args.fontsize,
            fade_duration=args.fade_duration,
            duration=args.duration,
        )

        clip.write_videofile(output, fps=args.fps, audio_codec="aac")

    def hello(self, args):
        # this routine will be called when "vidtoolz "textclip is called."
        print("Hello! This is an example ``vidtoolz`` plugin.")


textclip_plugin = ViztoolzPlugin()
