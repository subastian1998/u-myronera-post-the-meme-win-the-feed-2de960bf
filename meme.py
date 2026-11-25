"""Draw the meme for 'Post the Meme, Win the Feed' (make.fun).

Deterministic: fixed layout, no randomness, no timestamps. Writes a
1024x1024 PNG. Usage: python3 meme.py [output_path]  (default entry.png)
"""
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(sz):
    return ImageFont.truetype(BOLD, sz)


def caption(d, cx, y, text, fnt, fill, ol=(0, 0, 0), sw=5):
    d.text((cx, y), text, font=fnt, fill=fill, anchor="ma",
           stroke_width=sw, stroke_fill=ol)


def card(text, color, angle):
    c = Image.new("RGBA", (170, 100), (0, 0, 0, 0))
    cd = ImageDraw.Draw(c)
    cd.rounded_rectangle([4, 4, 166, 96], radius=14,
                         fill=(20, 28, 56, 255), outline=color, width=5)
    cd.text((85, 50), text, font=font(44), fill=color, anchor="mm")
    return c.rotate(angle, expand=True, resample=Image.BICUBIC)


def coin(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              fill=(255, 210, 63), outline=(176, 124, 0), width=4)
    d.text((cx, cy), "$", font=font(30), fill=(90, 60, 0), anchor="mm")


def main(out):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    # vertical gradient background
    top = (11, 16, 38)
    bot = (22, 32, 74)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)],
               fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    # fixed background stars
    for (x, y, r) in [(60, 120, 3), (150, 80, 2), (900, 100, 3),
                      (960, 200, 2), (80, 250, 2), (950, 300, 2),
                      (120, 900, 2), (920, 880, 3), (60, 700, 2),
                      (970, 620, 2)]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=(126, 139, 176))

    # top caption
    f76 = font(76)
    caption(d, 512, 46, "ME: I'LL JUST", f76, (255, 255, 255))
    caption(d, 512, 132, "ENTER ONE BOUNTY", f76, (255, 255, 255))

    # bounty cards on the sides
    for (cx, cy, text, color, angle) in [
            (150, 330, "$2", (57, 255, 130), -10),
            (150, 590, "$5", (57, 213, 255), 8),
            (874, 330, "$100", (255, 210, 63), 8)]:
        c = card(text, color, angle)
        img.paste(c, (cx - c.width // 2, cy - c.height // 2), c)
    d = ImageDraw.Draw(img)

    # coin stack, right side
    coin(d, 874, 560, 26)
    coin(d, 874, 615, 26)
    coin(d, 874, 670, 26)

    # robot head
    d.rounded_rectangle([302, 360, 322, 460], radius=8, fill=(159, 176, 204))  # left ear
    d.rounded_rectangle([702, 360, 722, 460], radius=8, fill=(159, 176, 204))  # right ear
    d.line([(512, 250), (512, 238)], fill=(159, 176, 204), width=10)
    d.ellipse([498, 214, 526, 242], fill=(57, 255, 130),
              outline=(0, 120, 60), width=4)  # antenna light
    d.rounded_rectangle([322, 250, 702, 530], radius=36,
                        fill=(201, 210, 228), outline=(90, 100, 130), width=6)
    # eyes
    d.rounded_rectangle([392, 340, 472, 402], radius=14, fill=(57, 213, 255),
                        outline=(10, 90, 130), width=4)
    d.rounded_rectangle([552, 340, 632, 402], radius=14, fill=(57, 213, 255),
                        outline=(10, 90, 130), width=4)
    d.ellipse([408, 352, 428, 372], fill=(255, 255, 255))
    d.ellipse([568, 352, 588, 372], fill=(255, 255, 255))
    # smile grill
    for yy in (452, 470, 488):
        d.line([(448, yy), (576, yy)], fill=(70, 80, 110), width=6)

    # shoulders / body
    d.rounded_rectangle([352, 530, 672, 640], radius=30,
                        fill=(159, 176, 204), outline=(90, 100, 130), width=5)
    # laptop with a rising chart on its screen
    d.rounded_rectangle([392, 600, 632, 692], radius=10,
                        fill=(20, 27, 51), outline=(70, 80, 120), width=4)
    d.rectangle([408, 612, 616, 668], fill=(10, 20, 40))
    d.line([(420, 656), (470, 640), (520, 646), (570, 622), (604, 622)],
           fill=(57, 255, 130), width=5, joint="curve")
    d.polygon([(604, 622), (592, 620), (600, 634)], fill=(57, 255, 130))

    # bottom caption
    f62 = font(62)
    caption(d, 512, 736, "12 BOUNTIES LATER:", f62, (255, 210, 63))
    caption(d, 512, 812, "I AM THE LEADERBOARD", f62, (255, 210, 63))
    d.text((512, 972), "make.fun", font=font(26),
           fill=(126, 139, 176), anchor="ma")

    img.save(out, format="PNG")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
