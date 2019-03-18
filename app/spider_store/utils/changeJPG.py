from PIL import Image


def change_jpg(before_path, after_path):
    im = Image.open(before_path)
    im.save(after_path)
