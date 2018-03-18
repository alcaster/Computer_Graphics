def translate_0_1_to_0_255(n: int) -> [float]:
    """
    Translate values f.ex 0,1,2 to [0, 127.5, 255]
    :param n: Specified number of element of return list
    :return: List with float values
    """
    return [i * (255 / (n - 1)) for i in range(n)]


def get_index_in_translation_0_1(val, ranges):
    """
    Given ranges from translate_0_1_to_0_255 check where number fit between.
    f.ex [0, 85, 170, 255] numer 90 fits in 1 gap.
    """
    for i in range(len(ranges)):
        if ranges[i] > val:
            return i - 1
