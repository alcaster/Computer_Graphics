import math
from copy import copy
import tkinter as tk
from utils.dataclasses import Point, Rectangle, EdgeBucket
from utils.cohen_utils import compute_outcode, Outcodes
from utils.list_utils import arrange_points_by_yx

canvas_width = 400
canvas_height = 400
python_green = "#476042"


class Board:
    def __init__(self, master, canvas):
        self.points = []
        self.canvas = canvas
        self.img = tk.PhotoImage(width=canvas_width, height=canvas_height)
        self.canvas.create_image((canvas_width // 2, canvas_height // 2), image=self.img, state="normal")

        self.master = master
        self.mode = self.cohen
        self.cohen_rectangle = None
        self.polygon = []

        canvas.bind("<Button-1>", self.paint)
        self.make_buttons()

    def make_buttons(self):
        button = tk.Button(master, text="Cohen-Sutherland", command=lambda: self.redraw(self.cohen))
        button.pack(side=tk.BOTTOM)
        button = tk.Button(master, text="Draw Poly", command=lambda: self.redraw(self.draw_poly))
        button.pack(side=tk.BOTTOM)
        button = tk.Button(master, text="Vertex Sorting", command=lambda: self.redraw(self.vertex_sorting))
        button.pack(side=tk.BOTTOM)
        button = tk.Button(master, text="Redraw", command=lambda: self.redraw)
        button.pack(side=tk.BOTTOM)

    def create_input(self, name):
        label = tk.IntVar()
        label.set(name)
        label_dir = tk.Label(self.master, textvariable=label, width=10)
        label_dir.pack()

    def paint(self, event):
        p1 = Point(event.x, event.y)
        self.try_create_pixel(p1, append=True)

        if self.mode == self.cohen:
            if not len(self.points) % 2:
                self.mode()
        else:
            self.mode()

    def try_create_pixel(self, p: Point, append: bool = False, color: str = '#ff0000'):
        if 0 < p.x < canvas_width and 0 < p.y < canvas_height:
            y = self.canvas.winfo_reqheight() - p.y if self.mode in [self.vertex_sorting, self.draw_poly] else p.y
            self.img.put(color, (p.x, y))
            if append:
                print(y)
                self.points.append(Point(p.x, y))

    def redraw(self, mode=None):
        previous_mode = self.mode
        if mode:
            self.mode = mode
        if previous_mode == self.draw_poly and mode == self.vertex_sorting:
            self.vertex_sorting()
            return
        self.points = []
        self.cohen_rectangle = None
        self.img = tk.PhotoImage(width=canvas_width, height=canvas_height)
        self.canvas.create_image((canvas_width // 2, canvas_height // 2), image=self.img, state="normal")

    def DDA(self, point1, point2, color='#ff0000'):
        # Pseudocode void lineDDA(int x1, int y1, int x2, int y2){float dy = y2 - y1;float dx = x2 - x1;float m = dy/dx;float y = y1;for (int x = x1; x <= x2; ++x){putPixel(x, round(y));y += m;}}
        p1, p2 = copy(point1), copy(point2)
        print(f"DDA from {p1} to {p2}")
        dy = p2.y - p1.y
        dx = p2.x - p1.x
        step = abs(dx if abs(dx) >= abs(dy) else dy)
        print(dx, dy, step)
        dx, dy = dx / step, dy / step
        while step > 0:
            self.try_create_pixel(Point(int(p1.x), int(p1.y)), color=color)
            p1.y += dy
            p1.x += dx
            step -= 1

    def cohen(self):
        if not self.cohen_rectangle:
            self.img = tk.PhotoImage(width=canvas_width, height=canvas_height)
            self.canvas.create_image((canvas_width // 2, canvas_height // 2), image=self.img, state="normal")
            p1, p3 = self.points[-2:]
            p2, p4 = Point(p3.x, p1.y), Point(p1.x, p3.y)
            print(f"Drawing rectangle from p1={p1} to p2={p2}")
            self.DDA(p1, p2)
            self.DDA(p2, p3)
            self.DDA(p3, p4)
            self.DDA(p4, p1)
            self.cohen_rectangle = Rectangle(p1.y, p3.x, p3.y, p1.x)
            return
        p1, p2 = self.points[-2:]
        clip = self.cohen_rectangle
        # From slides
        accept, done = False, False
        outcode1, outcode2 = compute_outcode(p1, clip), compute_outcode(p2, clip)
        while not done:
            print(f'{outcode1:b}, {outcode2:b}')
            if (outcode1 | outcode2) == 0:
                accept = True
                done = True

            elif (outcode1 & outcode2) != 0:
                accept = False
                done = True
            else:
                outcodeOut = outcode1 if outcode1 != 0 else outcode2
                p = Point(None, None)
                if (outcodeOut & Outcodes.TOP) != 0:
                    p.x = p1.x + (p2.x - p1.x) * (clip.top - p1.y) / (p2.y - p1.y)
                    p.y = clip.top
                elif (outcodeOut & Outcodes.BOTTOM) != 0:
                    p.x = p1.x + (p2.x - p1.x) * (clip.bottom - p1.y) / (p2.y - p1.y)
                    p.y = clip.bottom
                elif (outcodeOut & Outcodes.RIGHT) != 0:
                    p.y = p1.y + (p2.y - p1.y) * (clip.right - p1.x) / (p2.x - p1.x)
                    p.x = clip.right
                elif (outcodeOut & Outcodes.LEFT) != 0:
                    p.y = p1.y + (p2.y - p1.y) * (clip.left - p1.x) / (p2.x - p1.x)
                    p.x = clip.left
                if outcodeOut == outcode1:
                    p1 = p
                    outcode1 = compute_outcode(p1, clip)
                else:
                    p2 = p
                    outcode2 = compute_outcode(p2, clip)
        if accept:
            self.DDA(p1, p2)

    def vertex_sorting(self):
        if len(self.polygon) < 2:
            return
        for idx in range(len(self.polygon)):
            self.polygon[idx].idx = idx
        self.DDA(self.polygon[-1], self.polygon[0])
        sorted_points = arrange_points_by_yx(self.polygon)
        AET = []
        indices = [point.idx for point in sorted_points]

        k = 0
        i = indices[k]
        ymin = self.polygon[indices[0]].y
        ymax = self.polygon[indices[-1]].y
        y = ymin
        while y < ymax:
            while self.polygon[i].y == y:
                if self.polygon[i - 1].y > self.polygon[i].y:
                    AET.append(EdgeBucket(self.polygon[i - 1], self.polygon[i]))
                if self.polygon[(i + 1) % len(self.polygon)].y > self.polygon[i].y:
                    AET.append(EdgeBucket(self.polygon[(i + 1) % len(self.polygon)], self.polygon[i]))
                k += 1
                if k >= len(indices):
                    break
                i = indices[k]
            AET = sorted(AET, key=lambda e: e.x)
            for edge1, edge2 in self.iterate(AET):
                for x_iter in range(math.ceil(edge1.x), math.floor(edge2.x)):
                    self.try_create_pixel(Point(x_iter, y), color="#0000FF")

            y += 1
            AET = [edge for edge in AET if edge.ymax != y]
            for edge in AET:
                edge.x += edge.m_inverse

    @staticmethod
    def iterate(AET: [EdgeBucket]) -> [()]:
        return [(AET[idx], AET[idx + 1]) for idx in range(0, len(AET) - 1, 2)]

    def draw_poly(self):
        if self.polygon:
            self.DDA(self.polygon[-1], self.points[-1])
        self.polygon.append(self.points[-1])


@property
def modes(self):
    return {
        "DDA": self.DDA,
        "Edge Table": self.vertex_sorting,
        "Draw poly": self.draw_poly,
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
