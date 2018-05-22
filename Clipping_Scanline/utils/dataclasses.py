from dataclasses import dataclass


@dataclass
class Point:
    x: float
    y: float

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y


@dataclass
class Rectangle:
    top: float
    right: float
    bottom: float
    left: float


class EdgeBucket:

    def __init__(self, p1: Point, p2: Point):
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        self.m_inverse = dx / dy
        self.ymax = max(p1.y, p2.y)
        if p1.x > p2.x:
            self.x = p1.x if self.m_inverse < 0 else p2.x
        else:
            self.x = p2.x if self.m_inverse < 0 else p1.x

    def __str__(self):
        print(f"Edge bucket ymax:{self.ymax},x:{self.x},1/m:{self.m_inverse}")
