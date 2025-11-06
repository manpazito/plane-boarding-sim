"""Create an animated GIF from plain-text frame snapshots.

Usage (from repo root):
  python3 src/make_gif_from_text_frames.py \
      --frames-dir reports/animations --out reports/animations/animation.gif \
      --duration 80

The script uses Pillow (PIL). If Pillow is not installed, it will print a
friendly message asking to install it (pip install Pillow).
"""

import argparse
import glob
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    print("Pillow is required to run this script. Install with: pip install Pillow")
    raise


def render_text_to_image(
    text: str, font: ImageFont.ImageFont, padding=8, bg=(255, 255, 255), fg=(0, 0, 0)
):
    # Create a temporary image to measure text size
    lines = text.splitlines() or [""]
    max_width = 0
    total_height = 0
    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))

    # helper for compatibility across Pillow versions
    def _text_size(d, s, f):
        try:
            return d.textsize(s, font=f)
        except Exception:
            # newer Pillow versions: use textbbox
            bbox = d.textbbox((0, 0), s, font=f)
            return (bbox[2] - bbox[0], bbox[3] - bbox[1])

    for line in lines:
        w, h = _text_size(draw, line, font)
        max_width = max(max_width, w)
        total_height += h

    img = Image.new("RGB", (max_width + padding * 2, total_height + padding * 2), color=bg)  # type: ignore
    draw = ImageDraw.Draw(img)
    y = padding
    for line in lines:
        draw.text((padding, y), line, font=font, fill=fg)
        _, h = _text_size(draw, line, font)
        y += h
    return img


def make_gif(frames_dir: str, out_path: str, duration_ms: int = 150, font_path: str = None, font_size: int = 16, scale: int = 2):  # type: ignore
    # Accept either 'frame_00000.txt' or '{strategy}_frame_00000.txt' naming
    txt_files = sorted(glob.glob(os.path.join(frames_dir, "*frame_*.txt")))
    if not txt_files:
        print(f"No frames found in {frames_dir}")
        return 1

    # Choose font
    font = None
    if font_path and os.path.exists(font_path):
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception:
            font = None
    if font is None:
        # fallback to default monospaced-like font if available
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

    # Render each text frame to an image and compute max dimensions so we can
    # pad frames to a uniform canvas size (avoids jitter when frames differ).
    rendered = []
    max_w = 0
    max_h = 0
    for fn in txt_files:
        with open(fn, "r", encoding="utf-8") as fh:
            txt = fh.read()
        img = render_text_to_image(txt, font)  # type: ignore
        rendered.append(img)
        max_w = max(max_w, img.width)
        max_h = max(max_h, img.height)

    # Create final images with uniform size and optional scaling for a larger GIF
    images = []
    for img in rendered:
        base = Image.new("RGB", (max_w, max_h), color=(255, 255, 255))
        base.paste(img, (0, 0))
        if scale and scale != 1:
            base = base.resize(
                (base.width * scale, base.height * scale), resample=Image.NEAREST
            )
        images.append(base)

    # Save as GIF; use first image as base
    base = images[0]
    others = images[1:]
    # duration is per-frame in milliseconds
    base.save(
        out_path, save_all=True, append_images=others, duration=duration_ms, loop=0
    )
    print(f"Wrote GIF to {out_path} (frames: {len(images)})")
    return 0


def main(argv=sys.argv[1:]):
    p = argparse.ArgumentParser(description="Make GIF from text frames")
    p.add_argument(
        "--frames-dir",
        default="results/animations",
        help="Directory with frame_*.txt files",
    )
    p.add_argument(
        "--out", default="results/animations/animation.gif", help="Output GIF path"
    )
    p.add_argument("--duration", type=int, default=150, help="Frame duration in ms")
    p.add_argument("--font", default=None, help="Optional TTF font path")
    p.add_argument("--font-size", type=int, default=16, help="Font size for rendering")
    p.add_argument(
        "--scale",
        type=int,
        default=2,
        help="Integer scale factor to enlarge output images",
    )
    args = p.parse_args(argv)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    return make_gif(
        args.frames_dir,
        args.out,
        duration_ms=args.duration,
        font_path=args.font,
        font_size=args.font_size,
        scale=args.scale,
    )


if __name__ == "__main__":
    raise SystemExit(main())
