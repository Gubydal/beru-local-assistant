from PIL import ImageChops, ImageStat


def fingerprint(image, box=None):
    if box:
        w, h = image.size
        x, y, r, b = box
        image = image.crop((int(x * w), int(y * h), int(r * w), int(b * h)))
    return image.convert("L").resize((384, 192))


def changed(before, after):
    if before is None:
        return True
    diff = ImageChops.difference(before, after)
    return ImageStat.Stat(diff).mean[0] > 0.015 and diff.getextrema()[1] > 12
