from io import BytesIO
from PIL import Image
import numpy as np
import base64
from tqdm import tqdm

from src.utils.array_utils import translate_0_1_to_0_255, get_index_in_translation_0_1
from src.octree import OctreeNode


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


def average_dithering_n(img: np.ndarray, **kwargs):
    img = get_gray_image(img)
    shape = img.shape
    img_flatten = np.ndarray.flatten(img)
    if 'n' in kwargs:
        n = kwargs['n']
    else:
        return img

    ranges = translate_0_1_to_0_255(n)
    means = [img_flatten[(i < img_flatten) & (img_flatten < j)].mean() for i, j in zip(ranges, ranges[1:])]
    for pixel in tqdm(range(0, img_flatten.shape[0]), desc="Generating new img"):
        new_idx = get_index_in_translation_0_1(img_flatten[pixel], means) + 1
        # print(f"Ranges={ranges}, means={means}, new_idx={new_idx}, pixel={img_flatten[pixel]}")  # Debug
        img_flatten[pixel] = ranges[new_idx]  # Translate (from format 0,1,2) 2-> 255
    result = np.array(img_flatten).reshape(shape)
    return result


def ordered_dithering(img: np.ndarray, **kwargs):
    gray = get_gray_image(img)
    if 'n' in kwargs and 'k' in kwargs:
        n = kwargs['n']
        k = kwargs['k']
        result = gray.copy()
        bayer_matrix = create_bayer_matrix(n)
        ranges = translate_0_1_to_0_255(k)
        print(f"Bayer matrix {bayer_matrix}")
        for row_index in range(len(result)):
            for col_index in range(len(result[row_index])):
                pixel_value = result[row_index][col_index]
                threshold = bayer_matrix[row_index % n, col_index % n]
                c = threshold / (k - 1)
                m = [c + i * 255 / (k - 1) for i in range(k - 1)]
                # print(f"M = {m}")  # Debug
                if pixel_value >= m[-1]:
                    result[row_index][col_index] = ranges[-1]
                else:
                    for i in range(k - 1):
                        if pixel_value < m[i]:
                            result[row_index][col_index] = ranges[i]
                            break
        return result
    return img


def uniform_color_quantization(img: np.ndarray, **kwargs):
    if all(x in kwargs for x in ['kr', 'kg', 'kb']):
        kr = kwargs['kr']
        kg = kwargs['kg']
        kb = kwargs['kb']
    else:
        return img

    ranges_r = translate_0_1_to_0_255(kr + 1)
    ranges_g = translate_0_1_to_0_255(kg + 1)
    ranges_b = translate_0_1_to_0_255(kb + 1)
    ranges = [ranges_r, ranges_g, ranges_b]

    def quanization(pixel):
        new_pixel = [uniform_quantify_pixel(c, range) for c, range in zip(pixel, ranges)]
        return new_pixel

    new_img = np.apply_along_axis(quanization, -1, img)
    return new_img.astype(np.uint8)


def octree_color_quantization(img: np.ndarray, **kwargs):
    if 'n' in kwargs:
        n = kwargs['n']
    else:
        return img

    img = Image.fromarray(img)
    rootNode = OctreeNode(0, None)
    leafs_count = 0
    pixels = img.load()

    for i in tqdm(range(img.size[0]), desc="Adding colors"):
        for j in range(img.size[1]):
            is_inserted = rootNode.add(np.array(pixels[i, j]), 0)
            leafs_count += is_inserted

            while leafs_count > n:
                leaves = rootNode.get_leafs()
                max_depth = max([l.depth for l in leaves])
                toReduce = None
                for l in leaves:
                    if l.depth == max_depth:
                        if toReduce is None or l.parent.depth > len(toReduce.children):
                            toReduce = l.parent
                leafs_count -= toReduce.reduce_node()

    for l in rootNode.get_leafs():
        l.normalize_color()

    for i in tqdm(range(img.size[0]), desc="Transforming"):
        for j in range(img.size[1]):
            pixels[i, j] = tuple(rootNode.find_leaf_for_color(np.array(pixels[i, j]), 0).new_color)
    return np.array(img)


def bayer(n):
    if n == 2:
        return np.array([[1, 3], [4, 2]])
    if n == 3:
        return np.array([[3, 7, 4], [6, 1, 9], [2, 8, 5]])
    if n in [5, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 25, 26, 27, 28, 29, 30, 31]:
        raise Exception("N must be very specific.")
    return np.vstack((
        np.hstack((4 * (bayer(n / 2) - 1) + 1, 4 * (bayer(n / 2) - 1) + 3)),
        np.hstack((4 * (bayer(n / 2) - 1) + 4, 4 * (bayer(n / 2) - 1) + 2)),
    ))


def create_bayer_matrix(n):
    bayer_matrix = (1 / ((n * n) + 1)) * bayer(n)
    for y in tqdm(range(len(bayer_matrix)), desc="Creating bayer matrix"):
        for x in range(len(bayer_matrix)):
            bayer_matrix[x, y] = int(
                255 * ((bayer_matrix[x, y] + 0.5) / (len(bayer_matrix) * len(bayer_matrix))) * 10)
    return bayer_matrix.astype(dtype=np.uint8)


def uniform_quantify_pixel(val, ranges):
    translation = translate_0_1_to_0_255(len(ranges) - 1)
    return int(translation[get_index_in_translation_0_1(val, ranges)])


def get_gray_image(img):
    def pixel2gray(pixel):
        scale = [0.3, 0.6, 0.1]
        return sum([val * scal for val, scal in zip(pixel, scale)])

    return np.apply_along_axis(pixel2gray, -1, img)


def process_image(data: dict) -> np.ndarray:
    byte_img = data.pop("img")
    im = Image.open(BytesIO(base64.b64decode(byte_img)))
    numpy_image = np.asarray(im)
    print(f"Got image with shape {numpy_image.shape}")
    mode = data.pop("mode")
    if mode in modes:
        transformed = modes[mode](numpy_image, **data)
        return transformed
    return numpy_image


modes = {
    "inverse": inverse,
    "average_dithering": average_dithering,
    "average_dithering_n": average_dithering_n,
    "ordered_dithering": ordered_dithering,
    "uniform_color_quantization": uniform_color_quantization,
    "octree_color_quantization": octree_color_quantization,
}
