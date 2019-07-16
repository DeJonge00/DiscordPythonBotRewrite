from os import listdir
from random import choice


def get_image_from_folder(folder: str):
    im_name = choice(listdir(folder))
    return folder + "/" + im_name
