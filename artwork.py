#!/usr/bin/env python3
"""Deterministic generator for entry.png — a newspaper front page
summing up the world news of Thursday, 19 November 2026."""
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
CREAM = (248, 243, 230)
INK = (20, 16, 12)
RED = (179, 32, 42)
NAVY = (29, 53, 87)
GOLD = (212, 175, 55)
BLUE = (70, 130, 200)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = f"{FONT_DIR}/DejaVuSerif-Bold.ttf"
SANS = f"{FONT_DIR}/DejaVuSans.ttf"
SANS_BOLD = f"{FONT_DIR}/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, max_width, start_size, min_size=10):
    size = start_size
    while size > min_size:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 2
    return font(path, min_size)


def wrap(draw, text, f, max_width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=f) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def centered(draw, y, text, f, fill):
    w = draw.textlength(text, font=f)
    draw.text(((W - w) / 2, y), text, font=f, fill=fill)
    return y


def main():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img, "RGBA")
    margin = 48
    content_w = W - 2 * margin

    # --- Top small caps ---
    f_small = fit_font(draw, "THE WORLD'S NEWS  ·  IN ONE IMAGE", SANS_BOLD, content_w, 22)
    centered(draw, 26, "THE WORLD'S NEWS  ·  IN ONE IMAGE", f_small, INK)
    draw.line([(margin, 58), (W - margin, 58)], fill=INK, width=2)

    # --- Masthead ---
    f_mast = fit_font(draw, "WORLD TODAY", SERIF_BOLD, content_w, 108)
    centered(draw, 68, "WORLD TODAY", f_mast, INK)
    draw.line([(margin, 182), (W - margin, 182)], fill=INK, width=2)

    # --- Red date band ---
    draw.rectangle([margin, 192, W - margin, 238], fill=RED)
    f_date = fit_font(draw, "THURSDAY, NOVEMBER 19, 2026", SANS_BOLD, content_w - 20, 26)
    # vertically centre in band
    bbox = draw.textbbox((0, 0), "THURSDAY, NOVEMBER 19, 2026", font=f_date)
    th = bbox[3] - bbox[1]
    tw = draw.textlength("THURSDAY, NOVEMBER 19, 2026", font=f_date)
    draw.text(((W - tw) / 2, 192 + (46 - th) / 2 - bbox[1]), "THURSDAY, NOVEMBER 19, 2026", font=f_date, fill=WHITE)

    # --- Headline ---
    y = 254
    for line in ("THE SUMMIT", "OF THREE"):
        f_head = fit_font(draw, line, SERIF_BOLD, content_w, 84)
        centered(draw, y, line, f_head, INK)
        y += 88

    # --- Subhead ---
    subhead = ("Trump, Xi and Putin meet face to face in Shenzhen \u2014 the first "
               "trilateral summit of the three presidents, capping an APEC week "
               "that redrew the Pacific's diplomatic map.")
    f_sub = font(SANS, 21)
    y_sub = 434
    for line in wrap(draw, subhead, f_sub, content_w - 40):
        centered(draw, y_sub, line, f_sub, INK)
        y_sub += 27

    # --- Navy graphic band ---
    band_y0, band_y1 = 522, 668
    draw.rectangle([margin, band_y0, W - margin, band_y1], fill=NAVY)
    # gold sun
    draw.ellipse([770, band_y0 + 18, 850, band_y0 + 98], fill=GOLD)
    # skyline silhouette (deterministic)
    rng = random.Random(42)
    x = margin + 8
    buildings = []
    while x < W - margin - 30:
        bw = rng.randint(28, 52)
        bh = rng.randint(35, 80)
        buildings.append((x, band_y1 - 28 - bh, x + bw, band_y1 - 28))
        x += bw + rng.randint(4, 10)
    for (x0, y0, x1, y1) in buildings:
        draw.rectangle([x0, y0, x1, y1], fill=(10, 18, 32))
        # lit windows
        for wy in range(int(y0) + 6, int(y1) - 6, 12):
            for wx in range(int(x0) + 5, int(x1) - 5, 11):
                if rng.random() < 0.45:
                    draw.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 214, 90))
    # three overlapping circles for the three leaders
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    cy = band_y0 + 62
    od.ellipse([412, cy - 42, 496, cy + 42], fill=(179, 32, 42, 200))
    od.ellipse([470, cy - 42, 554, cy + 42], fill=(212, 175, 55, 200))
    od.ellipse([528, cy - 42, 612, cy + 42], fill=(70, 130, 200, 200))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(img, "RGBA")
    # caption strip at bottom of band
    draw.rectangle([margin, band_y1 - 28, W - margin, band_y1], fill=(10, 18, 32))
    f_cap = fit_font(draw, "KYLIN VILLA \u2014 FIRST TRILATERAL MEETS", SANS_BOLD, content_w - 20, 17)
    centered(draw, band_y1 - 23, "KYLIN VILLA \u2014 FIRST TRILATERAL MEETS", f_cap, WHITE)

    # --- Six stories: 2 rows x 3 columns ---
    stories = [
        ("NUCLEAR ARMS ON THE TABLE",
         "Trump presses for arms control at the trilateral; Beijing resists making it the centrepiece."),
        ("ENERGY'S DARKEST WARNING",
         "The IEA calls the Middle East crisis the greatest threat to energy security in history. Brent near $92."),
        ("TANKS CROSS THE LINE IN GAZA",
         "Israeli armour pushes past the ceasefire line in a rare operation to remove a threat."),
        ("EUROPE WATCHES FROM BERLIN",
         "Allied leaders gather as Ukraine's war nears five years \u2014 and its fate is debated without them."),
        ("A TRADE TRUCE RUNS OUT OF ROAD",
         "The US\u2013China truce expires on January 10; rare-earth exports sit 75% below normal."),
        ("TEHRAN: 'BIG LIES'",
         "Iran rejects US claims about its missile programme ahead of nuclear talks in Geneva."),
    ]
    col_gap = 22
    col_w = (content_w - 2 * col_gap) // 3
    rows_y = [686, 826]
    f_story_head = font(SANS_BOLD, 16)
    f_story_body = font(SANS, 15)
    for idx, (head, body) in enumerate(stories):
        row, col = divmod(idx, 3)
        x0 = margin + col * (col_w + col_gap)
        y0 = rows_y[row]
        if col > 0:
            draw.line([(x0 - col_gap // 2, y0), (x0 - col_gap // 2, y0 + 118)], fill=(180, 170, 150), width=1)
        yy = y0
        for line in wrap(draw, head, f_story_head, col_w):
            draw.text((x0, yy), line, font=f_story_head, fill=RED)
            yy += 20
        yy += 3
        for line in wrap(draw, body, f_story_body, col_w):
            draw.text((x0, yy), line, font=f_story_body, fill=INK)
            yy += 19
    # divider between rows
    draw.line([(margin, 812), (W - margin, 812)], fill=INK, width=1)
    draw.line([(margin, 682), (W - margin, 682)], fill=INK, width=1)

    # --- Footer ticker ---
    draw.line([(margin, 952), (W - margin, 952)], fill=INK, width=2)
    ticker = "XI PLEDGES $20M FOR ASIA-PACIFIC \u00b7 HONDURAS SENDS SPECIAL FORCES \u00b7 APEC PLENARY OPENS"
    f_tick = font(SANS_BOLD, 15)
    lines = wrap(draw, ticker, f_tick, content_w - 10)
    yy = 962
    for line in lines:
        centered(draw, yy, line, f_tick, RED)
        yy += 20

    out = Path(__file__).resolve().parent / "entry.png"
    img.save(out, "PNG", optimize=True)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
