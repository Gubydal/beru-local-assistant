from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from io import BytesIO
import textwrap, random

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"


def render(case, variant="clean"):
    stem_lines = len(textwrap.wrap(case["stem"], 95))
    option_lines = sum(
        len(textwrap.wrap(f"{chr(97 + i)}. {o}", 91)) * 24 + 8
        for i, o in enumerate(case["options"])
    )
    card_bottom = max(560, 286 + stem_lines * 23 + 25 + option_lines + 25)
    image = Image.new("RGB", (1280, max(720, card_bottom + 160)), "#f4f4ef")
    d = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT, 17)
    small = ImageFont.truetype(FONT, 14)
    title = ImageFont.truetype(FONT, 30)
    d.rectangle((0, 0, 1280, 45), fill="#075638")
    d.text(
        (35, 60), "moodle — ENCGT · page de test synthétique", font=font, fill="#4b4b4b"
    )
    d.text((30, 140), "Management interculturel & RSE", font=title, fill="#ae6057")
    d.rectangle((125, 270, 945, card_bottom), fill="#dcebed")
    d.text((25, 280), "Question 3", font=small, fill="#aa4840")
    d.text((975, 280), "Navigation du test", font=font, fill="#a86d59")
    d.text((975, 395), "Temps restant 0:00:42", font=small, fill="#777777")
    y = 286
    for line in textwrap.wrap(case["stem"], 95):
        d.text((145, y), line, font=font, fill="#40484a")
        y += 23
    y += 25
    for i, option in enumerate(case["options"]):
        d.ellipse(
            (145, y + 4, 154, y + 13),
            outline="#788585",
            fill=(
                "#1680bf"
                if variant == "selected_wrong"
                and i == ((case["gold"] or 0) + 1) % len(case["options"])
                else None
            ),
        )
        for line in textwrap.wrap(f"{chr(97 + i)}. {option}", 91):
            d.text((165, y), line, font=font, fill="#454c4d")
            y += 24
        y += 8
    d.rectangle((810, card_bottom + 40, 940, card_bottom + 78), fill="#47a3bc")
    d.text((818, card_bottom + 50), "Page suivante", font=small, fill="white")
    if variant == "question_only":
        return image.crop((125, 270, 945, card_bottom))
    if variant == "tiny":
        image = image.resize((768, 432))
    if variant == "blur":
        image = image.filter(ImageFilter.GaussianBlur(1.0))
    if variant == "heavy_blur":
        image = image.filter(ImageFilter.GaussianBlur(2.0))
    if variant == "low_contrast":
        image = ImageEnhance.Contrast(image).enhance(0.4)
    if variant == "dark":
        image = ImageEnhance.Brightness(image).enhance(0.45)
    if variant == "rotated":
        image = image.rotate(3, resample=Image.Resampling.BICUBIC, fillcolor="#282828")
    if variant == "jpeg":
        b = BytesIO()
        image.save(b, format="JPEG", quality=25)
        b.seek(0)
        image = Image.open(b).convert("RGB")
    if variant == "partial":
        image = image.crop((125, 270, 945, 365))
    if variant == "blank":
        image = Image.new("RGB", (820, 290), "white")
    if variant == "noise":
        rng = random.Random(42)
        for _ in range(12000):
            x = rng.randrange(image.width)
            y = rng.randrange(image.height)
            image.putpixel((x, y), (rng.randrange(256),) * 3)
    if variant == "severe_blur":
        image = image.filter(ImageFilter.GaussianBlur(3.5))
    if variant == "micro":
        image = image.resize((512, 288))
    if variant == "perspective":
        image = image.transform(
            image.size,
            Image.Transform.QUAD,
            (30, 5, 0, 690, 1250, 720, 1280, 35),
            resample=Image.Resampling.BICUBIC,
        )
    if variant == "moire":
        d = ImageDraw.Draw(image)
        for x in range(0, image.width, 4):
            d.line((x, 0, x + 70, image.height), fill=(190, 190, 180), width=1)
    if variant == "glare":
        import numpy as np

        array = np.array(image).astype(float)
        yy, xx = np.mgrid[: image.height, : image.width]
        glow = 0.7 * np.exp(
            -((xx - 600) ** 2 / (2 * 220**2) + (yy - 400) ** 2 / (2 * 150**2))
        )
        array = array * (1 - glow[:, :, None]) + 255 * glow[:, :, None]
        image = Image.fromarray(array.clip(0, 255).astype("uint8"))
    if variant == "cropped_choice":
        image = image.crop((125, 270, 945, 410))
    if variant == "retina":
        image = image.resize((2560, 1440))
    return image


VARIANTS = [
    "clean",
    "question_only",
    "selected_wrong",
    "tiny",
    "blur",
    "heavy_blur",
    "low_contrast",
    "dark",
    "rotated",
    "jpeg",
    "partial",
    "blank",
    "noise",
]
