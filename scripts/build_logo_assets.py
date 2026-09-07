import math
import os
from PIL import Image, ImageDraw, ImageFilter

SVG_CONTENT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="100%" height="100%">
  <defs>
    <!-- Background Dark Obsidian Gradient -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0A120D" />
      <stop offset="100%" stop-color="#12241A" />
    </linearGradient>

    <!-- Vivid Emerald-to-Lime Radiant Gradient for the C -->
    <linearGradient id="cGrad" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#22C55E" />
      <stop offset="50%" stop-color="#4ADE80" />
      <stop offset="100%" stop-color="#BEF264" />
    </linearGradient>

    <!-- Glowing Cyber Emerald Border -->
    <linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="rgba(74, 222, 128, 0.75)" />
      <stop offset="50%" stop-color="rgba(34, 197, 94, 0.45)" />
      <stop offset="100%" stop-color="rgba(190, 242, 100, 0.6)" />
    </linearGradient>

    <!-- Multi-stage Neon Drop Shadow / Glow -->
    <filter id="neonGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#4ADE80" flood-opacity="0.65" />
      <feDropShadow dx="0" dy="3" stdDeviation="12" flood-color="#22C55E" flood-opacity="0.35" />
    </filter>

    <filter id="badgeShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#000000" flood-opacity="0.5" />
    </filter>
  </defs>

  <!-- Rounded Squircle Badge Base -->
  <rect x="12" y="12" width="232" height="232" rx="58" fill="url(#bgGrad)" stroke="url(#borderGrad)" stroke-width="3" filter="url(#badgeShadow)" />

  <!-- Subtle Concentric Aperture Radar Rings -->
  <circle cx="128" cy="128" r="78" fill="none" stroke="rgba(74, 222, 128, 0.18)" stroke-width="1.5" stroke-dasharray="6 4" />
  <circle cx="128" cy="128" r="48" fill="none" stroke="rgba(74, 222, 128, 0.28)" stroke-width="1.5" />

  <!-- Center Reticle Core Dot -->
  <circle cx="128" cy="128" r="6.5" fill="#BEF264" opacity="0.95" />

  <!-- Bold Modern Geometric 'C' -->
  <path d="M 178 78
           A 68 68 0 1 0 178 178"
        fill="none"
        stroke="url(#cGrad)"
        stroke-width="28"
        stroke-linecap="round"
        filter="url(#neonGlow)" />

  <!-- Top Lens Flare Accent Dot -->
  <circle cx="128" cy="60" r="4" fill="#FFFFFF" opacity="0.95" />
</svg>"""

def main():
    # 1. Save SVG files
    with open("frontend/assets/logo.svg", "w", encoding="utf-8") as f:
        f.write(SVG_CONTENT)
    with open("app/assets/logo.svg", "w", encoding="utf-8") as f:
        f.write(SVG_CONTENT)
    print("Saved logo.svg in frontend and app")

    # 2. Render high-res raster assets using PIL
    size = 1024
    padding = 44
    r = 230

    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg)
    bg_draw.rounded_rectangle(
        [padding, padding, size - padding, size - padding],
        radius=r,
        fill=(10, 18, 13, 255),
        outline=(74, 222, 128, 160),
        width=12,
    )

    center = (size // 2, size // 2)
    outer_r = 310
    inner_r = 190

    bg_draw.ellipse(
        [center[0] - outer_r, center[1] - outer_r, center[0] + outer_r, center[1] + outer_r],
        outline=(74, 222, 128, 55),
        width=5,
    )
    bg_draw.ellipse(
        [center[0] - inner_r, center[1] - inner_r, center[0] + inner_r, center[1] + inner_r],
        outline=(74, 222, 128, 80),
        width=5,
    )

    c_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(c_layer)

    c_radius = 275
    c_width = 118

    start_deg = 36
    end_deg = 324
    num_points = 350

    for i in range(num_points + 1):
        ang_deg = start_deg + (end_deg - start_deg) * (i / num_points)
        ang_rad = math.radians(ang_deg)
        x = center[0] + c_radius * math.cos(ang_rad)
        y = center[1] + c_radius * math.sin(ang_rad)
        t = i / num_points
        if t < 0.5:
            st = t / 0.5
            cr = int(34 * (1 - st) + 74 * st)
            cg = int(197 * (1 - st) + 222 * st)
            cb = int(94 * (1 - st) + 128 * st)
        else:
            st = (t - 0.5) / 0.5
            cr = int(74 * (1 - st) + 190 * st)
            cg = int(222 * (1 - st) + 242 * st)
            cb = int(128 * (1 - st) + 100 * st)
        c_draw.ellipse(
            [x - c_width / 2, y - c_width / 2, x + c_width / 2, y + c_width / 2],
            fill=(cr, cg, cb, 255),
        )

    c_draw.ellipse(
        [center[0] - 24, center[1] - 24, center[0] + 24, center[1] + 24],
        fill=(190, 242, 100, 255),
    )
    flare_x = center[0]
    flare_y = center[1] - c_radius
    c_draw.ellipse(
        [flare_x - 16, flare_y - 16, flare_x + 16, flare_y + 16],
        fill=(255, 255, 255, 250),
    )

    glow = c_layer.filter(ImageFilter.GaussianBlur(radius=26))
    comp1 = Image.alpha_composite(bg, glow)
    final_im = Image.alpha_composite(comp1, c_layer)

    res256 = final_im.resize((256, 256), Image.Resampling.LANCZOS)
    res64 = final_im.resize((64, 64), Image.Resampling.LANCZOS)
    res48 = final_im.resize((48, 48), Image.Resampling.LANCZOS)
    res32 = final_im.resize((32, 32), Image.Resampling.LANCZOS)
    res16 = final_im.resize((16, 16), Image.Resampling.LANCZOS)

    res256.save("frontend/assets/favicon.png")
    res32.save("frontend/assets/favicon-32x32.png")
    res16.save("frontend/assets/favicon-16x16.png")

    res256.save("app/assets/favicon.png")
    res64.save("app/assets/favicon_64.png")

    # Multi-resolution ICO for perfect browser tab display
    res256.save(
        "frontend/assets/favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64)],
    )
    print("All favicon PNGs and ICO files successfully created!")

if __name__ == "__main__":
    main()
