from io import BytesIO
from PIL import Image
import numpy as np
import base64
from tqdm import tqdm

from src.utils.array_utils import translate_0_1_to_0_255, get_index_in_translation_0_1
from src.color import Color
from src.octree import OctreeQuantizer


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
        ranges = translate_0_1_to_0_255(n)
        means = [img_flatten[(i < img_flatten) & (img_flatten < j)].mean() for i, j in zip(ranges, ranges[1:])]
        print(means)
        for pixel in tqdm(range(0, img_flatten.shape[0]), desc="Generating new img"):
            # print(img_flatten[pixel], means, get_index_in_translation_0_1(img_flatten[pixel], means) + 1)  # DEBUG
            new_idx = get_index_in_translation_0_1(img_flatten[pixel], means) + 1
            img_flatten[pixel] = ranges[new_idx]  # Translate (from format 0,1,2) 2-> 255
        result = np.array(img_flatten).reshape(shape)
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
        for y in tqdm(range(height), desc='Changing pixels'):
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
    if all(x in kwargs for x in ['kr', 'kg', 'kb']):
        kr = kwargs['kr']
        kg = kwargs['kg']
        kb = kwargs['kb']

        ranges_r = translate_0_1_to_0_255(kr + 1)
        ranges_g = translate_0_1_to_0_255(kg + 1)
        ranges_b = translate_0_1_to_0_255(kb + 1)
        ranges = [ranges_r, ranges_g, ranges_b]

        def quanization(pixel):
            new_pixel = [uniform_quantify_pixel(c, range) for c, range in zip(pixel, ranges)]
            return new_pixel

        new_img = np.apply_along_axis(quanization, -1, img)
        return new_img.astype(np.uint8)
    return img


def octree_color_quantization(img: np.ndarray, **kwargs):
    image = Image.fromarray(img)
    pixels = image.load()
    width, height = image.size

    octree = OctreeQuantizer()

    # add colors to the octree
    for j in tqdm(range(height), desc="Adding colors to octree"):
        for i in range(width):
            r, g, b = pixels[i, j]
            octree.add_color(Color(int(r), int(g), int(b)))

    # 256 colors for 8 bits per pixel output image
    palette = octree.make_palette(256)
    print(f"Palette len = {len(palette)}, first entry {palette[0]}")
    # create palette for 256 color max and save to file
    palette_image = Image.new('RGB', (16, 16))
    palette_pixels = palette_image.load()
    for i, color in tqdm(enumerate(palette), desc="Creating palette for 256 colors"):
        palette_pixels[i % 16, i // 16] = (color.red, color.green, color.blue)
    palette_image.save('palette.png')

    # save output image
    out_image = Image.new('RGB', (width, height))
    out_pixels = out_image.load()
    for j in tqdm(range(height), desc="Creating new image"):
        for i in range(width):
            index = octree.get_palette_index(Color(*pixels[i, j]))
            color = palette[index]
            out_pixels[i, j] = (color.red, color.green, color.blue)
    return np.asarray(out_image)


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
