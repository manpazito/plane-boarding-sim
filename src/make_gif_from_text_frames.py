"""
Create an animated GIF from plain-text frame snapshots.

Usage example:
    python3 src/make_gif_from_text_frames.py \
        --frames-dir results/animations \
        --out results/animations/animation.gif \
        --duration 80

Requires Pillow (PIL):
    pip install Pillow
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import List, Optional, Tuple, TYPE_CHECKING

# Runtime Pillow imports
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image = None  # type: ignore
    ImageDraw = None  # type: ignore
    ImageFont = None  # type: ignore

# Type-checking imports (never executed at runtime)
if TYPE_CHECKING:
    from PIL.Image import Image as PILImage
    from PIL.ImageFont import FreeTypeFont as PILImageFont


RGBColor = Tuple[int, int, int]


def render_text_to_image(
    text: str,
    font: "PILImageFont",
    padding: int = 8,
    bg: RGBColor = (255, 255, 255),
    fg: RGBColor = (0, 0, 0),
) -> "PILImage":
    """Render a block of plain text into a PIL image with uniform padding."""

    # Ensure we have at least one line
    lines = text.splitlines() or [""]

    # Temporary img for measuring
    tmp_img = Image.new("RGB", (1, 1), color=bg)  # type: ignore
    draw = ImageDraw.Draw(tmp_img)  # type: ignore

    def _text_size(
        d: ImageDraw.ImageDraw, s: str, f: "PILImageFont"
    ) -> Tuple[int, int]:
        """Compatibility helper across Pillow versions."""
        try:
            return d.textsize(s, font=f)
        except Exception:
            bbox = d.textbbox((0, 0), s, font=f)
            return (bbox[2] - bbox[0], bbox[3] - bbox[1])

    max_width = 0
    total_height = 0
    for line in lines:
        w, h = _text_size(draw, line, font)
        max_width = max(max_width, w)
        total_height += h

    # Final image with padding
    img = Image.new(
        "RGB",
        (max_width + padding * 2, total_height + padding * 2),
        color=bg,
    )  # type: ignore

    draw = ImageDraw.Draw(img)  # type: ignore
    y = padding
    for line in lines:
        draw.text((padding, y), line, font=font, fill=fg)  # type: ignore
        _, h = _text_size(draw, line, font)
        y += h

    return img


def make_gif(
    frames_dir: Path,
    out_path: Path,
    duration_ms: int = 150,
    font_path: Optional[Path] = None,
    font_size: int = 16,
    scale: int = 2,
) -> int:
    """Create a GIF from a directory of text-frame files."""

    # Check for Pillow
    if Image is None or ImageDraw is None or ImageFont is None:
        print("Pillow is required. Install with: pip install Pillow")
        return 1

    if scale < 1:
        print("Scale factor must be >= 1.")
        return 1

    frames_dir = frames_dir.resolve()
    out_path = out_path.resolve()

    if not frames_dir.is_dir():
        print(f"Frames directory does not exist: {frames_dir}")
        return 1

    # Detect frames like frame_00001.txt or back_to_front_frame_00001.txt
    txt_files = sorted(frames_dir.glob("*frame_*.txt"))
    if not txt_files:
        print(f"No frame text files found in: {frames_dir}")
        return 1

    # Load font if provided, otherwise fallback
    font: Optional["PILImageFont"] = None
    if font_path:
        font_path = font_path.expanduser()
        if font_path.is_file():
            try:
                font = ImageFont.truetype(str(font_path), font_size)  # type: ignore
            except Exception:
                print(f"Warning: Failed to load font at {font_path}, using default.")
                font = None

    if font is None:
        try:
            font = ImageFont.load_default()  # type: ignore
        except Exception:
            print("Error: Could not load default font from Pillow.")
            return 1

    # Render frames
    rendered: List["PILImage"] = []
    max_w, max_h = 0, 0

    for fn in txt_files:
        with fn.open("r", encoding="utf-8") as fh:
            txt = fh.read()
        img = render_text_to_image(txt, font)
        rendered.append(img)
        max_w = max(max_w, img.width)
        max_h = max(max_h, img.height)

    # Normalize sizes and scale
    final_images: List["PILImage"] = []
    for img in rendered:
        base = Image.new("RGB", (max_w, max_h), color=(255, 255, 255))  # type: ignore
        base.paste(img, (0, 0))
        if scale != 1:
            base = base.resize(
                (base.width * scale, base.height * scale),
                resample=Image.NEAREST,
            )
        final_images.append(base)

    # Save animated GIF
    out_path.parent.mkdir(parents=True, exist_ok=True)
    first, rest = final_images[0], final_images[1:]

    first.save(
        out_path,
        save_all=True,
        append_images=rest,
        duration=duration_ms,
        loop=0,
    )

    print(f"Wrote GIF to {out_path} (frames: {len(final_images)})")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a GIF from text-frame snapshots."
    )
    parser.add_argument(
        "--frames-dir",
        default="results/animations",
        help="Directory containing '*frame_*.txt' files.",
    )
    parser.add_argument(
        "--out", default="results/animations/animation.gif", help="Output GIF file."
    )
    parser.add_argument(
        "--duration", type=int, default=150, help="Milliseconds per frame."
    )
    parser.add_argument("--font", default=None, help="Optional TTF font file.")
    parser.add_argument("--font-size", type=int, default=16, help="Font size.")
    parser.add_argument(
        "--scale", type=int, default=2, help="Integer scaling factor for output size."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    args = parse_args(argv)

    frames_dir = Path(args.frames_dir)
    out_path = Path(args.out)
    font_path = Path(args.font) if args.font else None

    return make_gif(
        frames_dir=frames_dir,
        out_path=out_path,
        duration_ms=args.duration,
        font_path=font_path,
        font_size=args["font_size"] if hasattr(args, "font_size") else args.font_size,
        scale=args.scale,
    )


if __name__ == "__main__":
    raise SystemExit(main())
