from io import BytesIO
from PIL import Image
import numpy as np
import base64

from src.utils.array_utils import translate_0_1_to_0_255


def inverse(img: np.ndarray, **kwargs):
    return 255 - img


def average_dithering(img: np.ndarray, **kwargs):
    img = get_gray_image(img)
    shape = img.shape
    threshold = int(np.mean(img))
    img = np.ndarray.flatten(img)
    for pixel in range(0, img.shape[0]):
        img[pixel] = 255 if img[pixel] > threshold else 0
    result = np.array(img).reshape(shape)
    return result


def ordered_dithering(img: np.ndarray, **kwargs):
    gray = get_gray_image(img)
    height, width = gray.shape
    if 'n' in kwargs and 'k' in kwargs:
        n = kwargs['n']
        k = kwargs['k']
        bayer = create_bayer_matrix(n)
        print(bayer)
        result = gray.copy()
        for y in range(height):
            for x in range(width):
                threshold = bayer[x % n, y % n]
                values = translate_0_1_to_0_255(k)
                if k == 2:
                    result[y, x] = values[0] if gray[y, x] < threshold else values[1]
                elif k == 4:
                    threshold1 = max(0, threshold - int(threshold / 2))
                    threshold2 = threshold
                    threshold3 = min(255, threshold + int(threshold / 2))
                    if gray[y, x] < threshold1:
                        result[y, x] = values[0]
                    elif threshold2 > gray[y, x] >= threshold1:
                        result[y, x] = values[1]
                    elif threshold3 > gray[y, x] >= threshold2:
                        result[y, x] = values[2]
                    elif gray[y, x] >= threshold3:
                        result[y, x] = values[3]
        return result

    return img


def uniform_color_quantization(img: np.ndarray, **kwargs):
    return NotImplementedError


def octree_color_quantization(img: np.ndarray, **kwargs):
    return NotImplementedError


def dither(n):
    if n == 2:
        return np.array([[1, 3], [4, 2]])
    if n == 3:
        return np.array([[3, 7, 4], [6, 1, 9], [2, 8, 5]])
    if n in [5, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 25, 26, 27, 28, 29, 30, 31]:
        raise Exception("N must be very specific.")
    return np.vstack((
        np.hstack((4 * (dither(n / 2) - 1) + 1, 4 * (dither(n / 2) - 1) + 3)),
        np.hstack((4 * (dither(n / 2) - 1) + 4, 4 * (dither(n / 2) - 1) + 2)),
    ))


def create_bayer_matrix(n):
    bayer_matrix = (1 / ((n * n) + 1)) * dither(n)
    for y in range(len(bayer_matrix)):
        for x in range(len(bayer_matrix)):
            bayer_matrix[x, y] = int(
                255 * ((bayer_matrix[x, y] + 0.5) / (len(bayer_matrix) * len(bayer_matrix))) * 10)
    return bayer_matrix.astype(dtype=np.uint8)


def get_gray_image(img):
    def pixel2gray(pixel):
        scale = [0.3, 0.6, 0.1]
        return sum([val * scal for val, scal in zip(pixel, scale)])

    return np.apply_along_axis(pixel2gray, -1, img)


def process_image(data: dict) -> np.ndarray:
    byte_img = data.pop("img")
    im = Image.open(BytesIO(base64.b64decode(byte_img)))
    numpy_image = np.asarray(im)
    mode = data.pop("mode")
    if mode in modes:
        transformed = modes[mode](numpy_image, **data)
        return transformed
    return numpy_image


modes = {
    "inverse": inverse,
    "average_dithering": average_dithering,
    "ordered_dithering": ordered_dithering,
    "octree_color_quantization": octree_color_quantization,
}
