from utils.dataclasses import Point, Rectangle


class Outcodes:
    LEFT = 1
    RIGHT = 2
    BOTTOM = 4
    TOP = 8


def compute_outcode(p: Point, clip: Rectangle) -> int:
    outcode = 0
    if p.x > clip.right:
        outcode |= Outcodes.RIGHT
    elif p.x < clip.left:
        outcode |= Outcodes.LEFT
    if p.y < clip.top:
        outcode |= Outcodes.TOP
    elif p.y > clip.bottom:
        outcode |= Outcodes.BOTTOM
    return outcode
