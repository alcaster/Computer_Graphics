def translate_0_1_to_0_255(n: int) -> [float]:
    """
    Translate values f.ex 0,1,2 to [0, 127.5, 255]
    :param n: Specified number of element of return list
    :return: List with float values
    """
    l = [0]
    for i in range(1, n):
        l.append(l[i - 1] + 255 / (n - 1))
    return l
