import itertools
import math

import tkinter as tk
import numpy as np

from DrawingCanvas.utils.dataclasses import Point
from DrawingCanvas.utils.list_utils import arrange_points

canvas_width = 400
canvas_height = 400
python_green = "#476042"


class Board:
    def __init__(self, master, canvas):
        self.i = 0
        self.points = []
        self.canvas = canvas
        self.img = tk.PhotoImage(width=canvas_width, height=canvas_height)
        self.canvas.create_image((canvas_width // 2, canvas_height // 2), image=self.img, state="normal")

        self.master = master
        self.mode = self.DDA

        canvas.bind("<Button-1>", self.paint)
        self.make_buttons()

    def make_buttons(self):
        button = tk.Button(master, text="Drawing with pen", command=lambda: self.redraw(self.drawing_with_pen))
        button.pack(side=tk.BOTTOM)
        button = tk.Button(master, text="Gupta Sproull", command=lambda: self.redraw(self.gupta_sproull))
        button.pack(side=tk.BOTTOM)
        button = tk.Button(master, text="Midpointv2", command=lambda: self.redraw(self.midpoint_circle_v2))
        button.pack(side=tk.BOTTOM)
        button = tk.Button(master, text="DDA", command=lambda: self.redraw(self.DDA))
        button.pack(side=tk.BOTTOM)
        button = tk.Button(master, text="Redraw", command=self.redraw)
        button.pack(side=tk.BOTTOM)
        self.create_input("Radius")
        self.radius = tk.Entry(self.master, width=5)
        self.radius.pack()
        self.create_input("Brush size")
        self.brush_size = tk.Entry(self.master, width=5)
        self.brush_size.pack()
        self.create_input("thickness")
        self.thickness = tk.Entry(self.master, width=5)
        self.thickness.pack()

    def create_input(self, name):
        label = tk.IntVar()
        label.set(name)
        label_dir = tk.Label(self.master, textvariable=label, width=10)
        label_dir.pack()

    def paint(self, event):
        p1 = Point(event.x, event.y)
        print(p1)
        self.i += 1
        self.try_create_pixel(p1)

        if self.mode in [self.DDA, self.drawing_with_pen, self.gupta_sproull]:
            if not len(self.points) % 2:
                self.mode()
        else:
            self.mode()

    def try_create_pixel(self, p: Point, color='#000000'):
        if 0 < p.x < canvas_width and 0 < p.y < canvas_height:
            self.img.put(color, (p.x, p.y))
            self.points.append(p)

    def redraw(self, mode=None):
        self.points = []
        self.img = tk.PhotoImage(width=canvas_width, height=canvas_height)
        self.canvas.create_image((canvas_width // 2, canvas_height // 2), image=self.img, state="normal")
        if mode:
            self.mode = mode

    def DDA(self):
        # Pseudocode void lineDDA(int x1, int y1, int x2, int y2){float dy = y2 - y1;float dx = x2 - x1;float m = dy/dx;float y = y1;for (int x = x1; x <= x2; ++x){putPixel(x, round(y));y += m;}}
        p1, p2 = arrange_points(self.points[-2:])
        print(f"DDA from {p1} to {p2}")
        dy = p2.y - p1.y
        dx = p2.x - p1.x
        step = abs(dx if dx >= abs(dy) else dy)
        dx, dy = dx / step, dy / step
        while step > 0:
            self.try_create_pixel(Point(int(p1.x), int(p1.y)))
            p1.y += dy
            p1.x += dx
            step -= 1

    def draw_circle_point(self, x: int, y: int, p: Point):
        self.try_create_pixel(Point(p.x + x, p.y + y), '#000000')
        self.try_create_pixel(Point(p.x + y, p.y + x), '#000000')
        self.try_create_pixel(Point(p.x - y, p.y + x), '#000000')
        self.try_create_pixel(Point(p.x - x, p.y + y), '#000000')
        self.try_create_pixel(Point(p.x - x, p.y - y), '#000000')
        self.try_create_pixel(Point(p.x - y, p.y - x), '#000000')
        self.try_create_pixel(Point(p.x + y, p.y - x), '#000000')
        self.try_create_pixel(Point(p.x + x, p.y - y), '#000000')

    def midpoint_circle_v2(self):
        # Midpoint Circle v. 2 - addition only (s. 17) void MidpointCircle(int R) { int d = 1-R; int x = 0; int y = R; putPixel(x, y); while (y > x) { if ( d < 0 ) //move to E d += 2*x + 3; else //move to SE { d += 2*x - 2*y + 5; --y; } ++x; putPixel(x, y); } }
        p = self.points[-1]
        R = int(self.radius.get() or 0)
        print(f"Midpoint_circle_v2 center: {p}, radius: {R}")

        dx = 1
        dy = 1
        diameter = R * 2
        diff = dx - diameter

        x, y = R - 1, 0
        while x >= y:
            self.draw_circle_point(int(x), int(y), p)
            if diff <= 0:
                y += 1
                diff += dy
                dy += 2
            else:
                x -= 1
                dx += 2
                diff += dx - diameter

    def gupta_sproull(self):
        # Gupta-Sproull - lines with thickness (s. 22-29)
        p1, p2 = arrange_points(self.points[-2:])
        print(f"Gupta-Sproull from {p1} to {p2}")

        thickness = int(self.thickness.get() or 5)

        dx = p2.x - p1.x
        dy = p2.y - p1.y
        dE = 2 * dy
        dNE = 2 * (dy - dx)
        d = 2 * dy - dx

        # two_v_dx = 0
        invDenom = 1 / (2 * math.sqrt(dx ** 2 + dy ** 2))
        two_dx_invDenom = 2 * dx * invDenom

        x, y = p1.x, p1.y

        self.intensify_pixel(p1, thickness, 0)
        for sign in [-1, 1]:
            for i in itertools.count():
                if self.intensify_pixel(Point(x, y + i * sign), thickness, i * two_dx_invDenom) == 0:
                    break

        while x < p2.x:
            x += 1
            if d < 0:
                two_v_dx = d + dx
                d += dE
            else:
                two_v_dx = d - dx
                d += dNE
                y += 1

            self.intensify_pixel(p1, thickness, 0)
            for sign in [-1, 1]:
                for i in itertools.count():
                    if self.intensify_pixel(Point(x, y + i * sign), thickness,
                                            i * two_dx_invDenom - two_v_dx * invDenom * sign) == 0:
                        break

    def intensify_pixel(self, p: Point, thickness, distance):
        print(f"{p}. Distance: {distance}")
        r = 0.5
        cov = self.coverage(thickness, abs(distance), r)
        print(f'Coverage: {cov}')
        if cov > 0:
            rgb = ([255 - int(cov * 255) for _ in range(3)])
            # print(rgb)
            color = "#%02x%02x%02x" % tuple(rgb)
            self.try_create_pixel(p, color)
        return cov

    def coverage(self, thickness, D, r):
        w = thickness / 2

        if w >= r:
            # print("The line is thicker than the pixel")
            return self.cov(D - w, r) if w <= D else 1 - self.cov(w - D, r)

        if 0 <= D <= w:
            return 1 - self.cov(w - D, r) - self.cov(w + D, r)
        elif w <= D <= r - w:
            return self.cov(D - w, r) - self.cov(D + w, r)
        else:
            return self.cov(D - w, r)

    @staticmethod
    def cov(d, r):
        # Math domain errors
        # a = math.acos(d / r)  # Math domain error 3.0
        # b = math.sqrt(r ** 2 - d ** 2) # math domain error -2
        return 1 / math.pi * math.acos(d / r) - d / (math.pi * r ** 2) * math.sqrt(
            r ** 2 - d ** 2) if -1 <= d / r <= 1 and r ** 2 - d ** 2 > 0 else 0

    @staticmethod
    def rect_matrix(n):
        """
        N must be odd
        """
        upper_triangle = [(i * 2) + 1 for i in range(n // 2)]
        counts = upper_triangle + [n] + upper_triangle[::-1]
        matrix = np.zeros((n, n))

        for i, count in zip(range(n), counts):
            for j in range(count):
                matrix[i][(n - count) // 2 + j] = 1
        print(matrix)
        return matrix

    def drawing_with_pen(self):
        p1, p2 = self.points[-2:]
        dx, dy = p2.x - p1.x, p2.y - p1.y
        step = abs(dx if abs(dx) >= abs(dy) else dy)
        dx, dy = dx / step, dy / step

        brush_size = int(self.brush_size.get() or 0)
        matrix = self.rect_matrix(brush_size)
        print(f'drawing from {p1} to {p2}, brush size: {brush_size}')

        while step > 0:
            idx = int(len(matrix) / 2)

            for i in range(len(matrix)):
                for j in range(len(matrix[i])):
                    if matrix[i][j] != 0:
                        new_point = Point(int(p1.x - idx + i), int(p1.y - int(len(matrix[i]) / 2) + j))
                        self.try_create_pixel(new_point)
            p1.y += dy
            p1.x += dx
            step -= 1

    @property
    def modes(self):
        return {
            "DDA": self.DDA,
            "Midpointv2": self.midpoint_circle_v2,
            "Gupta-Sproull": self.gupta_sproull,
            "Drawing with pen": self.drawing_with_pen,
        }


if __name__ == '__main__':
    master = tk.Tk()
    master.title("Canvas Drawing")
    w = tk.Canvas(master,
                  width=canvas_width,
                  height=canvas_height, bd=5, highlightthickness=0, relief='ridge')
    w.pack()
    b = Board(master, w)

    tk.mainloop()
