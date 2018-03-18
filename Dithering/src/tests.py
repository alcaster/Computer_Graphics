from PIL import Image
import numpy as np

from src.image_processing import uniform_color_quantization
from src.utils.matplot_utils import show_images

PATH = "../../data/images/eye.jpg"


def uniform_color_quantization_test(org):
    processed = uniform_color_quantization(org, kr=3, kg=3, kb=3)
    show_images([org, processed])


def main():
    org = np.asarray(Image.open(PATH))

    uniform_color_quantization_test(org)


if __name__ == '__main__':
    main()
