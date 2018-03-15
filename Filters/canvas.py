from tkinter import *
import collections
from functools import partial

canvas_width = 256
canvas_height = 256
python_green = "#476042"
points = {}
real_values = {}


def paint(canvas, event):
    x1, y1 = (event.x - 1), (event.y - 1)
    x2, y2 = (event.x + 1), (event.y + 1)
    create_dot(x1, y1, x2, y2, canvas)
    redraw(canvas)


def create_dot(x1, y1, x2, y2, canvas):
    canvas.create_line(x1, y1, x2, y2, fill=python_green)
    points[x1] = y1


def create_lines_between_dots(canvas):
    sorted_points = collections.OrderedDict(sorted(points.items()))
    for p1, p2 in zip(list(sorted_points), list(sorted_points)[1:]):
        canvas.create_line(p1, points[p1], p2, points[p2])


def redraw(canvas):
    canvas.delete("all")
    for px, py in points.items():
        create_dot(px, py, px + 1, py + 1, canvas)
    create_lines_between_dots(canvas)


def calculate_real_values():
    """Takes points and calculate value for each point"""
    sorted_points = collections.OrderedDict(sorted(points.items()))
    for p1, p2 in zip(list(sorted_points), list(sorted_points)[1:]):
        slope = (points[p2] - points[p1]) / (p2 - p1)
        current_value = points[p1]
        for i in range(p2 - p1 + 1):
            real_values[p1 + i] = current_value
            current_value += slope


if __name__ == '__main__':
    master = Tk()
    master.title("Painting using Ovals")
    w = Canvas(master,
               width=canvas_width,
               height=canvas_height)
    w.pack()
    create_dot(0, 255, 1, 256, w)
    create_dot(255, 0, 256, 1, w)
    create_lines_between_dots(w)
    paint_with_canvas = partial(paint, w)
    w.bind("<B1-Motion>", paint_with_canvas)

    message = Label(master, text="Insert point to modify grapg")
    message.pack(side=BOTTOM)

    mainloop()
