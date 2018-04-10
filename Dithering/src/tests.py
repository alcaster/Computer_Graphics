from PIL import Image
import numpy as np

from src.image_processing import uniform_color_quantization, octree_color_quantization, average_dithering_n
from src.utils.matplot_utils import show_images

PATH = "../../data/images/eye.jpg"


def uniform_color_quantization_test(org):
    processed = uniform_color_quantization(org, kr=3, kg=3, kb=3)
    show_images([org, processed])


def octree_test(org):
    processed = octree_color_quantization(org, n=50)
    processed = np.array(processed)
    show_images([org, processed])


def average_dithering_n_test(org):
    processed = average_dithering_n(org, n=3)
    show_images([org, processed])


def main():
    org = np.asarray(Image.open(PATH))
    octree_test(org)
    # average_dithering_n_test(org)


if __name__ == '__main__':
    main()
