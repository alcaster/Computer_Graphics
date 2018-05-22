from utils.dataclasses import Point


def arrange_points_by_x(points: [Point], reverse=False)->[Point]:
    return sorted(points, key=lambda p: p.x, reverse=reverse)


def arrange_points_by_yx(points: [Point], reverse=False)->[Point]:
    return sorted(points, key=lambda p: [p.y, p.x], reverse=reverse)


def arrange_points_by_y(points: [Point], reverse=False)->[Point]:
    return sorted(points, key=lambda p: p.y, reverse=reverse)
