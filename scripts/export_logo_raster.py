"""Rasterize logo.svg to logo.jpg and favicon.png using Pillow (simple redraw)."""
import math
import pathlib

from PIL import Image, ImageDraw

ROOT = pathlib.Path(r"f:\강아지보호소품으로")
ASSETS = ROOT / "site" / "assets"


def draw_logo(size: int) -> Image.Image:
    img = Image.new("RGB", (size, size), "#f4efe6")
    d = ImageDraw.Draw(img)
    pad = size * 0.06
    r = size * 0.24
    d.rounded_rectangle([pad, pad, size - pad, size - pad], radius=r, fill="#2f6b4a")
    cx, cy = size / 2, size * 0.54
    cr = size * 0.36
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill="#fffdf9")
    bw = max(2, size // 45)
    d.ellipse(
        [cx - size * 0.22, cy - size * 0.06, cx + size * 0.22, cy + size * 0.24],
        fill="#f4efe6",
        outline="#241c16",
        width=bw,
    )
    for ex in (cx - size * 0.14, cx + size * 0.14):
        d.ellipse(
            [ex - size * 0.08, cy - size * 0.18, ex + size * 0.08, cy + size * 0.02],
            fill="#ebe3d4",
            outline="#241c16",
            width=bw,
        )
    pr = size * 0.055
    d.ellipse([cx - pr, cy + size * 0.04 - pr, cx + pr, cy + size * 0.04 + pr], fill="#e15a32")
    star_y = size * 0.22
    star_r = size * 0.06
    points = []
    for i in range(5):
        ang = math.radians(-90 + i * 72)
        points.append((cx + star_r * math.cos(ang), star_y + star_r * math.sin(ang)))
        ang2 = math.radians(-90 + i * 72 + 36)
        points.append((cx + star_r * 0.42 * math.cos(ang2), star_y + star_r * 0.42 * math.sin(ang2)))
    d.polygon(points, fill="#e15a32")
    return img


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    large = draw_logo(512)
    large.save(ASSETS / "logo.jpg", quality=92, optimize=True)
    small = draw_logo(64)
    small.save(ASSETS / "favicon.png", optimize=True)
    print("wrote logo.jpg favicon.png")


if __name__ == "__main__":
    main()
