"""
Render a clean bold-C CreditLens logo to PNG/ICO using PIL only.
No external SVG renderer needed.
"""
import math
from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
PADDING = 40
RADIUS = 220  # squircle corner radius


def make_logo(size: int = 1024) -> Image.Image:
    pad = int(PADDING * size / 1024)
    r = int(RADIUS * size / 1024)

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Dark squircle background — gradient approximated with solid
    draw.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=r,
        fill=(11, 22, 14, 255),
    )

    # Draw the C using a thick arc (open circle, ~300° sweep, gap on the right)
    cx, cy = size // 2, size // 2

    # Stroke width and arc radius
    stroke = int(size * 0.125)        # ~128px at 1024
    arc_r = int(size * 0.33)          # ~338px radius

    # Draw filled arc by layering circles along the arc path
    # Gap: 60° to the right => arc from 60° to 300° (240° sweep) on standard coords
    # PIL angles: 0=right, 90=bottom, 180=left, 270=top
    start_angle = 50    # degrees
    end_angle = 310     # degrees
    num_steps = 400

    for i in range(num_steps + 1):
        t = i / num_steps
        angle_deg = start_angle + (end_angle - start_angle) * t
        angle_rad = math.radians(angle_deg)

        px = cx + arc_r * math.cos(angle_rad)
        py = cy + arc_r * math.sin(angle_rad)

        # Gradient: lime green (#7EDB5A) at top → forest green (#4A9E2F) at bottom
        # t=0 → top-right terminal, t=1 → bottom-right terminal
        # Use y-position for gradient direction
        gy = (py - (cy - arc_r)) / (2 * arc_r)  # 0=top, 1=bottom
        gy = max(0.0, min(1.0, gy))
        cr = int(126 * (1 - gy) + 74 * gy)   # 126→74
        cg = int(219 * (1 - gy) + 158 * gy)  # 219→158
        cb = int(90 * (1 - gy) + 47 * gy)    # 90→47

        half = stroke // 2
        draw.ellipse(
            [px - half, py - half, px + half, py + half],
            fill=(cr, cg, cb, 255),
        )

    return img


def main():
    full = make_logo(1024)

    sizes = {
        "frontend/assets/favicon.png":    256,
        "frontend/assets/favicon-32x32.png": 32,
        "frontend/assets/favicon-16x16.png": 16,
        "app/assets/favicon.png":         256,
        "app/assets/favicon_64.png":       64,
    }

    for path, sz in sizes.items():
        full.resize((sz, sz), Image.Resampling.LANCZOS).save(path)
        print(f"  saved {path} ({sz}x{sz})")

    # Multi-size ICO
    res256 = full.resize((256, 256), Image.Resampling.LANCZOS)
    res256.save(
        "frontend/assets/favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64)],
    )
    print("  saved frontend/assets/favicon.ico (multi-size)")
    print("Done.")


if __name__ == "__main__":
    main()
