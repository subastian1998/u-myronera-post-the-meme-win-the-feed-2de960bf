"""Draw the meme for 'Post the Meme, Win the Feed' (make.fun).

Redesigned visuals, same concept and same text: robot enters one bounty,
ends up leaderboard king. Deterministic: fixed layout, fixed-seed PRNG
only, no timestamps, no network. Writes a 1024x1024 PNG.
Usage: python3 meme.py [output_path]  (default entry.png)
"""
import math
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1024
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(sz):
    return ImageFont.truetype(BOLD, sz)


def caption(d, cx, y, text, fnt, fill, ol=(0, 0, 0), sw=5):
    d.text((cx, y), text, font=fnt, fill=fill, anchor="ma",
           stroke_width=sw, stroke_fill=ol)


def glow_text(base, cx, y, text, fnt, fill, glow_rgb, blur=8):
    """Draw text with a soft glow underlay, then crisp text on top."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.text((cx, y), text, font=fnt, fill=glow_rgb + (255,),
            anchor="ma", stroke_width=6, stroke_fill=(60, 35, 0, 255))
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(ov)
    d = ImageDraw.Draw(base)
    d.text((cx, y), text, font=fnt, fill=fill + (255,), anchor="ma",
           stroke_width=5, stroke_fill=(0, 0, 0, 255))


def radial_blob(size, rgb, max_alpha):
    """RGBA square with a radial alpha falloff (nebula glow)."""
    blob = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = blob.load()
    c = size / 2.0
    for yy in range(size):
        for xx in range(size):
            dist = math.hypot(xx - c, yy - c) / c
            if dist < 1.0:
                a = int(max_alpha * (1.0 - dist) ** 2)
                px[xx, yy] = (rgb[0], rgb[1], rgb[2], a)
    return blob


def card(text, color, angle):
    c = Image.new("RGBA", (170, 100), (0, 0, 0, 0))
    cd = ImageDraw.Draw(c)
    cd.rounded_rectangle([4, 4, 166, 96], radius=14,
                         fill=(20, 28, 56, 255), outline=color, width=5)
    # glossy top sheen
    cd.rounded_rectangle([10, 10, 160, 34], radius=10,
                         fill=(255, 255, 255, 38))
    cd.text((85, 52), text, font=font(44), fill=color, anchor="mm")
    return c.rotate(angle, expand=True, resample=Image.BICUBIC)


def card_glow(color, angle):
    g = Image.new("RGBA", (210, 140), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    gd.rounded_rectangle([20, 20, 190, 120], radius=18,
                         fill=color + (110,))
    g = g.filter(ImageFilter.GaussianBlur(14))
    return g.rotate(angle, expand=True, resample=Image.BICUBIC)


def coin(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              fill=(255, 210, 63), outline=(176, 124, 0), width=4)
    d.ellipse([cx - r + 6, cy - r + 5, cx - r + 12, cy - r + 11],
              fill=(255, 240, 170))
    d.text((cx, cy), "$", font=font(30), fill=(90, 60, 0), anchor="mm")


def sparkle(d, cx, cy, r, fill=(255, 255, 255)):
    d.polygon([(cx, cy - r), (cx + r // 3, cy - r // 3),
               (cx + r, cy), (cx + r // 3, cy + r // 3),
               (cx, cy + r), (cx - r // 3, cy + r // 3),
               (cx - r, cy), (cx - r // 3, cy - r // 3)], fill=fill)


def crown_layer():
    c = Image.new("RGBA", (240, 110), (0, 0, 0, 0))
    cd = ImageDraw.Draw(c)
    gold = (255, 210, 63)
    dark = (176, 124, 0)
    # three spikes with ball tips
    cd.polygon([(15, 95), (35, 28), (70, 66), (120, 14), (170, 66),
                (205, 28), (225, 95)], fill=gold, outline=dark, width=4)
    for (tx, ty) in [(35, 24), (120, 10), (205, 24)]:
        cd.ellipse([tx - 9, ty - 9, tx + 9, ty + 9],
                   fill=gold, outline=dark, width=3)
    # gems on the band
    for (gx, col) in [(70, (255, 80, 90)), (120, (80, 200, 255)),
                      (170, (255, 80, 90))]:
        cd.ellipse([gx - 7, 72, gx + 7, 86], fill=col, outline=dark, width=2)
    cd.rectangle([15, 88, 225, 98], fill=(230, 170, 30), outline=dark, width=3)
    return c.rotate(-12, expand=True, resample=Image.BICUBIC)


def confetti_piece(color, angle):
    c = Image.new("RGBA", (18, 9), (0, 0, 0, 0))
    cd = ImageDraw.Draw(c)
    cd.rectangle([1, 1, 17, 8], fill=color)
    return c.rotate(angle, expand=True, resample=Image.BICUBIC)


def trophy_layer():
    c = Image.new("RGBA", (120, 110), (0, 0, 0, 0))
    cd = ImageDraw.Draw(c)
    cx, top = 60, 8
    gold = (255, 210, 63)
    dark = (176, 124, 0)
    # handles
    cd.ellipse([cx - 50, top + 8, cx - 26, top + 38], outline=gold, width=5)
    cd.ellipse([cx + 26, top + 8, cx + 50, top + 38], outline=gold, width=5)
    # cup
    cd.polygon([(cx - 32, top), (cx + 32, top), (cx + 22, top + 52),
                (cx - 22, top + 52)], fill=gold, outline=dark, width=3)
    cd.line([(cx - 26, top + 8), (cx - 18, top + 44)],
            fill=(255, 240, 170), width=4)
    # stem + base
    cd.rectangle([cx - 6, top + 52, cx + 6, top + 74], fill=gold,
                 outline=dark, width=2)
    cd.rectangle([cx - 24, top + 74, cx + 24, top + 86], fill=gold,
                 outline=dark, width=2)
    cd.rectangle([cx - 18, top + 86, cx + 18, top + 94], fill=(230, 170, 30),
                 outline=dark, width=2)
    sparkle(cd, cx + 42, top + 6, 9)
    return c


def main(out):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    # rich 3-stop vertical gradient: deep navy -> purple-blue -> indigo
    stops = [(8, 10, 34), (20, 16, 62), (36, 22, 84)]
    for y in range(H):
        t = y / (H - 1)
        if t < 0.5:
            a, b, u = stops[0], stops[1], t / 0.5
        else:
            a, b, u = stops[1], stops[2], (t - 0.5) / 0.5
        d.line([(0, y), (W, y)],
               fill=tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3)))

    # nebula glow blobs (layered translucent radial gradients)
    base = img.convert("RGBA")
    for (cx, cy, size, rgb, alpha) in [
            (180, 180, 640, (120, 60, 180), 70),
            (860, 780, 600, (40, 180, 190), 60),
            (830, 140, 560, (60, 90, 220), 55),
            (120, 820, 520, (190, 60, 140), 45)]:
        blob = radial_blob(size, rgb, alpha)
        base.alpha_composite(blob, (cx - size // 2, cy - size // 2))
    img = base.convert("RGB")
    d = ImageDraw.Draw(img)

    # many more stars, varied size and brightness (fixed seed: deterministic)
    rng = random.Random(20261125)
    star_cols = [(255, 255, 255), (200, 220, 255), (255, 240, 190),
                 (160, 200, 255)]
    for _ in range(80):
        x = rng.randint(15, 1009)
        y = rng.randint(15, 1009)
        r = rng.choice([1, 1, 2, 2, 3, 4])
        col = rng.choice(star_cols)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        if r >= 3:
            sparkle(d, x, y, r + 5, fill=col)

    # vignette: darken the corners
    vg = Image.new("L", (256, 256), 0)
    vp = vg.load()
    for yy in range(256):
        for xx in range(256):
            dist = math.hypot(xx - 127.5, yy - 127.5) / 127.5
            vp[xx, yy] = int(max(0.0, dist - 0.62) / 0.38 * 105) if dist > 0.62 else 0
    vg = vg.resize((W, H), Image.BICUBIC)
    black = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.composite(black, img, vg)
    d = ImageDraw.Draw(img)

    # top caption (same text), raised so the crown clears it
    f76 = font(76)
    caption(d, 512, 36, "ME: I'LL JUST", f76, (255, 255, 255))
    caption(d, 512, 112, "ENTER ONE BOUNTY", f76, (255, 255, 255))

    # bounty cards with soft outer glow, stronger tilt
    for (cx, cy, text, color, angle) in [
            (150, 330, "$2", (57, 255, 130), -14),
            (150, 590, "$5", (57, 213, 255), 12),
            (874, 330, "$100", (255, 210, 63), 12)]:
        g = card_glow(color, angle)
        img.paste(g, (cx - g.width // 2, cy - g.height // 2), g)
        c = card(text, color, angle)
        img.paste(c, (cx - c.width // 2, cy - c.height // 2), c)
    d = ImageDraw.Draw(img)

    # gold coins spilling out of the $100 card
    coin(d, 812, 392, 14)
    coin(d, 848, 400, 12)
    coin(d, 882, 390, 13)

    # coin stack, right side
    coin(d, 874, 560, 26)
    coin(d, 874, 615, 26)
    coin(d, 874, 670, 26)

    # soft shadow under the robot body
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse([360, 636, 664, 668], fill=(0, 0, 0, 70))
    ov = ov.filter(ImageFilter.GaussianBlur(6))
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img)

    # robot ears
    d.rounded_rectangle([302, 360, 322, 460], radius=8, fill=(159, 176, 204))
    d.rounded_rectangle([702, 360, 722, 460], radius=8, fill=(159, 176, 204))

    # antenna on the right side of the head, glowing with a halo
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse([596, 196, 644, 244], fill=(57, 255, 130, 70))
    od.ellipse([604, 204, 636, 236], fill=(57, 255, 130, 120))
    ov = ov.filter(ImageFilter.GaussianBlur(5))
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img)
    d.line([(620, 252), (620, 238)], fill=(159, 176, 204), width=10)
    d.ellipse([606, 212, 634, 240], fill=(57, 255, 130),
              outline=(0, 120, 60), width=4)
    d.ellipse([612, 218, 622, 228], fill=(255, 255, 255))

    # golden crown, tilted and scaled down, sitting on the head
    # (top of the crown clears the top caption)
    cr = crown_layer()
    cr = cr.resize((int(cr.width * 0.78), int(cr.height * 0.78)),
                   Image.LANCZOS)
    img.paste(cr, (450 - cr.width // 2, 248 - cr.height // 2), cr)
    d = ImageDraw.Draw(img)

    # robot head with metallic shading
    d.rounded_rectangle([322, 250, 702, 530], radius=36,
                        fill=(201, 210, 228), outline=(90, 100, 130), width=6)
    # top sheen
    d.line([(352, 262), (640, 262)], fill=(238, 242, 252), width=4)
    # right-side shade
    d.rounded_rectangle([668, 262, 694, 518], radius=12, fill=(178, 188, 210))
    d.rounded_rectangle([322, 250, 702, 530], radius=36,
                        outline=(90, 100, 130), width=6)

    # bigger glowing eyes with sparkle highlights
    for (ex0, ex1) in [(388, 478), (546, 636)]:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.rounded_rectangle([ex0 - 12, 323, ex1 + 12, 420], radius=20,
                             fill=(57, 213, 255, 70))
        ov = ov.filter(ImageFilter.GaussianBlur(8))
        img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"),
                  (0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([ex0, 335, ex1, 408], radius=16,
                            fill=(57, 213, 255), outline=(10, 90, 130), width=4)
        d.ellipse([ex0 + 14, 347, ex0 + 36, 369], fill=(255, 255, 255))
        sparkle(d, ex0 + 52, 352, 9)
        d.ellipse([ex1 - 30, 384, ex1 - 14, 400], fill=(190, 245, 255))

    # rosy cheek blush
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse([366, 424, 408, 448], fill=(255, 150, 180, 95))
    od.ellipse([616, 424, 658, 448], fill=(255, 150, 180, 95))
    ov = ov.filter(ImageFilter.GaussianBlur(3))
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img)

    # confident smirk (replaces the plain grill lines)
    pts = []
    for i in range(31):
        t = i / 30.0
        x = 448 + (582 - 448) * t
        # quadratic bezier: start (448,478), control (520,496), end (582,450)
        y = (1 - t) ** 2 * 478 + 2 * (1 - t) * t * 496 + t ** 2 * 450
        pts.append((x, y))
    d.line(pts, fill=(70, 80, 110), width=8, joint="curve")
    d.ellipse([578, 442, 590, 454], fill=(70, 80, 110))  # dimple

    # shoulders / body
    d.rounded_rectangle([352, 530, 672, 640], radius=30,
                        fill=(159, 176, 204), outline=(90, 100, 130), width=5)
    d.line([(380, 542), (640, 542)], fill=(190, 205, 228), width=4)
    # laptop with a rising chart on its screen
    d.rounded_rectangle([392, 600, 632, 692], radius=10,
                        fill=(20, 27, 51), outline=(70, 80, 120), width=4)
    d.rectangle([408, 612, 616, 668], fill=(10, 20, 40))
    d.line([(420, 656), (470, 640), (520, 646), (570, 622), (604, 622)],
           fill=(57, 255, 130), width=5, joint="curve")
    d.polygon([(604, 622), (592, 620), (600, 634)], fill=(57, 255, 130))

    # confetti pieces around the robot
    conf = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for (cx, cy, col, ang) in [
            (280, 300, (255, 210, 63), 25), (744, 296, (57, 255, 130), -30),
            (272, 520, (57, 213, 255), 40), (752, 520, (255, 210, 63), -15),
            (330, 180, (57, 255, 130), -45), (700, 180, (255, 210, 63), 20),
            (250, 650, (255, 210, 63), 55), (772, 660, (57, 213, 255), -40),
            (420, 706, (57, 213, 255), 10), (604, 706, (255, 210, 63), -25),
            (296, 420, (255, 210, 63), -60), (728, 430, (57, 255, 130), 35),
            (300, 255, (57, 213, 255), 65), (664, 236, (255, 210, 63), -50)]:
        p = confetti_piece(col, ang)
        conf.alpha_composite(p, (cx - p.width // 2, cy - p.height // 2))
    img = Image.alpha_composite(img.convert("RGBA"), conf).convert("RGB")
    d = ImageDraw.Draw(img)

    # small golden trophy at the far left of the bottom text block,
    # clear of both bottom lines ("12..." starts x=150, "I AM..." x=87)
    tr = trophy_layer()
    tr = tr.resize((84, 77), Image.LANCZOS)
    img.paste(tr, (0, 762), tr)

    # bottom caption with a soft glow so it pops (same text)
    rgba = img.convert("RGBA")
    f62 = font(62)
    glow_text(rgba, 512, 736, "12 BOUNTIES LATER:", f62, (255, 210, 63),
              (150, 95, 0))
    glow_text(rgba, 512, 812, "I AM THE LEADERBOARD", f62, (255, 210, 63),
              (150, 95, 0))
    img = rgba.convert("RGB")
    d = ImageDraw.Draw(img)
    d.text((512, 972), "make.fun", font=font(26),
           fill=(126, 139, 176), anchor="ma")

    img.save(out, format="PNG")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
