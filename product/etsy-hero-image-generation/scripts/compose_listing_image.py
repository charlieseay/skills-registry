#!/usr/bin/env python3
"""
Deterministic compositor for Etsy hero / "what's included" images.

The AI model only paints a TEXT-FREE backdrop (fal_generate.py). Everything a
buyer has to be able to read or trust - the product name, the claims, the badges,
the actual product pages - is placed here with PIL, so it is spelled correctly
and shows the real deliverable (digital-product-quality-bar s.2: the hero shows
the actual product, never an abstract cover graphic).

Usage:  compose_listing_image.py spec.json
Spec (all coordinates are on a 3000x3000 canvas):
{
  "out": "hero.jpg", "size": 3000, "background": "bg-fal-hero.png",
  "palette": {"primary": "#2f5d50", "accent": "#e8a0a8", "ink": "#1f2a28",
              "panel": "#fbf7f2", "on_primary": "#ffffff"},
  "layout": "hero" | "grid",
  "title": ["52 WEEK", "SAVINGS CHALLENGE"],   "tagline": "...",
  "pages": ["p1.png", ...],                      # real product page renders
  "page_mode": "single" | "fan",
  "badges": ["FILLABLE PDF", "INSTANT DOWNLOAD", "PRINT-READY"],
  "seal": ["54", "FILLABLE", "FIELDS"],          # round corner badge, optional
  "cards": [{"title": "...", "color": "#hex", "items": ["..."], "thumb": "p.png"}],  # grid layout
  "footer": "spec line"
}
"""
import json, sys, os, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AVENIR = "/System/Library/Fonts/Avenir Next.ttc"   # 0 Bold, 2 Demi, 5 Medium, 8 Heavy
FACES = {"heavy": 8, "bold": 0, "demi": 2, "medium": 5, "regular": 7}


def font(size, face="bold"):
    return ImageFont.truetype(AVENIR, size, index=FACES[face])


def hexrgb(h, a=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def fit_font(draw, text, face, max_w, start, min_size=40):
    s = start
    while s > min_size and draw.textlength(text, font=font(s, face)) > max_w:
        s -= 4
    return font(s, face)


def shadowed(img, radius=40, offset=(0, 30), opacity=110):
    """Return (RGBA image with soft drop shadow, pad)."""
    pad = radius * 3
    w, h = img.size
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", (w, h), (0, 0, 0, opacity))
    canvas.paste(sh, (pad + offset[0], pad + offset[1]), sh)
    canvas = canvas.filter(ImageFilter.GaussianBlur(radius))
    canvas.paste(img, (pad, pad), img)
    return canvas, pad


def page_card(path, width, border=0):
    im = Image.open(path).convert("RGBA")
    h = int(im.height * width / im.width)
    im = im.resize((width, h), Image.LANCZOS)
    if border:
        framed = Image.new("RGBA", (width + border * 2, h + border * 2), (255, 255, 255, 255))
        framed.paste(im, (border, border), im)
        im = framed
    return im


def paste_center(base, im, cx, cy, angle=0, shadow=True):
    if angle:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    if shadow:
        im, _ = shadowed(im)
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def pill(draw, x, y, text, fnt, fill, fg, padx=60, pady=30):
    tw = draw.textlength(text, font=fnt)
    asc, desc = fnt.getmetrics()
    h = asc + desc + pady * 2
    w = tw + padx * 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h / 2, fill=fill)
    draw.text((x + padx, y + pady), text, font=fnt, fill=fg)
    return w, h


def pills_row(draw, y, badges, pal, size, max_w=2800, gap=40):
    fnt = font(size, "demi")
    widths = [draw.textlength(b, font=fnt) + 120 for b in badges]
    while sum(widths) + gap * (len(badges) - 1) > max_w and size > 40:
        size -= 4
        fnt = font(size, "demi")
        widths = [draw.textlength(b, font=fnt) + 120 for b in badges]
    x = (3000 - (sum(widths) + gap * (len(badges) - 1))) / 2
    for b, w in zip(badges, widths):
        pill(draw, x, y, b, fnt, hexrgb(pal["primary"]), hexrgb(pal["on_primary"]))
        x += w + gap


def seal(base, cx, cy, r, lines, pal):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hexrgb(pal["accent"]),
              outline=hexrgb(pal["on_primary"]), width=14)
    sizes = [int(r * 0.62)] + [int(r * 0.24)] * (len(lines) - 1)
    faces = ["heavy"] + ["demi"] * (len(lines) - 1)
    heights = [sum(font(s, f).getmetrics()) for s, f in zip(sizes, faces)]
    y = cy - sum(heights) / 2 - r * 0.04
    for t, s, f, h in zip(lines, sizes, faces, heights):
        fnt = fit_font(d, t, f, r * 1.55, s)
        d.text((cx - d.textlength(t, font=fnt) / 2, y), t, font=fnt, fill=hexrgb(pal["accent_ink"]))
        y += h
    sh, pad = shadowed(layer.crop((cx - r - 20, cy - r - 20, cx + r + 20, cy + r + 20)), radius=25, offset=(0, 15))
    base.alpha_composite(sh, (int(cx - r - 20 - pad), int(cy - r - 20 - pad)))


def title_panel(base, spec, pal, top=110, height=None):
    """Rounded panel with 1-2 title lines + tagline; returns bottom y."""
    d = ImageDraw.Draw(base)
    m = spec.get("panel_margin", 150)
    lines = spec["title"]
    fonts = [fit_font(d, t, "heavy", 2500, 250 if i == len(lines) - 1 else 200) for i, t in enumerate(lines)]
    tag_f = fit_font(d, spec.get("tagline", ""), "medium", 2500, 100) if spec.get("tagline") else None
    hs = [sum(f.getmetrics()) for f in fonts]
    tag_h = sum(tag_f.getmetrics()) + 30 if tag_f else 0
    ph = height or (sum(hs) + tag_h + 150)
    panel = Image.new("RGBA", base.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([m, top, 3000 - m, top + ph], radius=70, fill=hexrgb(pal["panel"], 238))
    sh, pad = shadowed(panel.crop((m, top, 3000 - m, top + ph)), radius=30, offset=(0, 18), opacity=70)
    base.alpha_composite(sh, (m - pad, top - pad))
    y = top + 70
    for t, f, h, i in zip(lines, fonts, hs, range(len(lines))):
        col = pal["primary"] if i == len(lines) - 1 else pal["ink"]
        d.text(((3000 - d.textlength(t, font=f)) / 2, y), t, font=f, fill=hexrgb(col))
        y += h
    if tag_f:
        y += 20
        t = spec["tagline"]
        d.text(((3000 - d.textlength(t, font=tag_f)) / 2, y), t, font=tag_f, fill=hexrgb(pal["ink"]))
    return top + ph


def hero(base, spec, pal):
    bottom = title_panel(base, spec, pal)
    pages = spec["pages"]
    badge_y = 2700
    area_top, area_bot = bottom + 60, badge_y - 60
    cy = (area_top + area_bot) / 2
    avail_h = area_bot - area_top
    if spec.get("page_mode", "single") == "single" or len(pages) == 1:
        im = Image.open(pages[0])
        w = int(min(1500, avail_h * 0.95 * im.width / im.height))
        paste_center(base, page_card(pages[0], w, border=spec.get("page_border", 0)), 1500, cy, spec.get("angle", 0))
    else:
        n = len(pages)
        im = Image.open(pages[0])
        w = int(min(1100, avail_h * 0.86 * im.width / im.height))
        spread = spec.get("spread", 1700)
        for i, p in enumerate(pages):
            t = (i / (n - 1)) - 0.5 if n > 1 else 0
            angle = -t * spec.get("fan_angle", 18)
            cx = 1500 + t * spread
            yoff = abs(t) * 90
            paste_center(base, page_card(p, w, border=spec.get("page_border", 0)), cx, cy + yoff, angle)
    d = ImageDraw.Draw(base)
    if spec.get("badges"):
        pills_row(d, badge_y, spec["badges"], pal, 78)
    if spec.get("seal"):
        sx, sy = spec.get("seal_pos", [2560, bottom + 330])
        seal(base, sx, sy, 270, spec["seal"], pal)


def grid(base, spec, pal):
    # frosted overlay so dense text stays readable over the photo
    ov = Image.new("RGBA", base.size, hexrgb(pal["panel"], 200))
    base.alpha_composite(ov)
    d = ImageDraw.Draw(base)
    f = fit_font(d, spec["title"][0], "heavy", 2600, 190)
    d.text(((3000 - d.textlength(spec["title"][0], font=f)) / 2, 120), spec["title"][0], font=f, fill=hexrgb(pal["primary"]))
    y0 = 120 + sum(f.getmetrics()) + 10
    if spec.get("tagline"):
        tf = fit_font(d, spec["tagline"], "medium", 2600, 90)
        d.text(((3000 - d.textlength(spec["tagline"], font=tf)) / 2, y0), spec["tagline"], font=tf, fill=hexrgb(pal["ink"]))
        y0 += sum(tf.getmetrics()) + 70
    cards = spec["cards"]
    cols = spec.get("cols", 3)
    rows = math.ceil(len(cards) / cols)
    footer_h = 260 if spec.get("footer") else 60
    gap = 50
    cw = (3000 - 200 - gap * (cols - 1)) / cols
    ch = (3000 - y0 - footer_h - gap * (rows - 1)) / rows
    for i, c in enumerate(cards):
        r, k = divmod(i, cols)
        # centre a short last row
        in_row = min(cols, len(cards) - r * cols)
        xoff = (cols - in_row) * (cw + gap) / 2
        x = 100 + xoff + k * (cw + gap)
        y = y0 + r * (ch + gap)
        card = Image.new("RGBA", (int(cw), int(ch)), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=50, fill=(255, 255, 255, 250))
        col = hexrgb(c.get("color", pal["primary"]))
        band = 150 if c.get("title") else 0
        if band:
            cd.rounded_rectangle([0, 0, cw - 1, band + 50], radius=50, fill=col)
            cd.rectangle([0, band, cw - 1, band + 50], fill=(255, 255, 255, 250))
            tf = fit_font(cd, c["title"], "heavy", cw - 80, 80)
            cd.text(((cw - cd.textlength(c["title"], font=tf)) / 2, (band - sum(tf.getmetrics())) / 2 + 5),
                    c["title"], font=tf, fill=(255, 255, 255, 255))
        yy = band + 40
        if c.get("thumb"):
            th_h = int((ch - band - 60) * c.get("thumb_ratio", 0.55 if c.get("items") else 0.80))
            th = Image.open(c["thumb"]).convert("RGBA")
            tw = int(th.width * th_h / th.height)
            if tw > cw - 80:
                tw = int(cw - 80); th_h = int(th.height * tw / th.width)
            th = th.resize((tw, th_h), Image.LANCZOS)
            cd.rectangle([(cw - tw) / 2 - 4, yy - 4, (cw + tw) / 2 + 4, yy + th_h + 4], outline=(210, 210, 210, 255), width=4)
            card.alpha_composite(th, (int((cw - tw) / 2), int(yy)))
            yy += th_h + 40
            if c.get("caption"):
                cf = fit_font(cd, c["caption"], "demi", cw - 60, 72)
                cd.text(((cw - cd.textlength(c["caption"], font=cf)) / 2, yy), c["caption"], font=cf, fill=hexrgb(pal["ink"]))
                yy += sum(cf.getmetrics()) + 20
        items = c.get("items", [])
        if items:
            isz = c.get("item_size", 62)
            longest = max(items, key=lambda t: cd.textlength(t, font=font(isz, "medium")))
            f_it = fit_font(cd, longest, "medium", cw - 150, isz)
            lh = sum(f_it.getmetrics()) + 14
            for it in items:
                cd.ellipse([50, yy + lh / 2 - 16, 78, yy + lh / 2 + 12], fill=col)
                cd.text((105, yy), it, font=f_it, fill=hexrgb(pal["ink"]))
                yy += lh
        sh, pad = shadowed(card, radius=25, offset=(0, 14), opacity=60)
        base.alpha_composite(sh, (int(x - pad), int(y - pad)))
    if spec.get("footer"):
        ff = fit_font(d, spec["footer"], "demi", 2700, 80)
        fw = d.textlength(spec["footer"], font=ff)
        fh = sum(ff.getmetrics())
        yb = 3000 - footer_h + 60
        d.rounded_rectangle([(3000 - fw) / 2 - 70, yb, (3000 + fw) / 2 + 70, yb + fh + 60], radius=(fh + 60) / 2, fill=hexrgb(pal["primary"]))
        d.text(((3000 - fw) / 2, yb + 30), spec["footer"], font=ff, fill=hexrgb(pal["on_primary"]))


def main():
    spec = json.load(open(sys.argv[1]))
    base_dir = os.path.dirname(os.path.abspath(sys.argv[1]))
    rel = lambda p: p if os.path.isabs(p) else os.path.join(base_dir, p)
    spec["pages"] = [rel(p) for p in spec.get("pages", [])]
    for c in spec.get("cards", []):
        if c.get("thumb"):
            c["thumb"] = rel(c["thumb"])
    pal = {"primary": "#2f5d50", "accent": "#e8a0a8", "accent_ink": "#ffffff", "ink": "#1f2a28",
           "panel": "#fbf7f2", "on_primary": "#ffffff", **spec.get("palette", {})}
    S = spec.get("size", 3000)
    bg = Image.open(rel(spec["background"])).convert("RGBA").resize((3000, 3000), Image.LANCZOS)
    base = bg.copy()
    (grid if spec.get("layout") == "grid" else hero)(base, spec, pal)
    out = rel(spec["out"])
    img = base.convert("RGB")
    if S != 3000:
        img = img.resize((S, S), Image.LANCZOS)
    img.save(out, "JPEG", quality=92, optimize=True)
    print(out, img.size, f"{os.path.getsize(out)/1e6:.2f}MB")


if __name__ == "__main__":
    main()
