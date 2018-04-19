import tkinter as tk

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
        self.master = master
        self.mode = self.DDA

        canvas.bind("<Button-1>", self.paint)
        self.make_buttons()

    def make_buttons(self):
        button = tk.Button(master, text="Redraw", command=self.redraw)
        button.pack(side=tk.BOTTOM)
        button = tk.Button(master, text="DDA", command=lambda: self.redraw("DDA"))
        button.pack(side=tk.BOTTOM)
        button = tk.Button(master, text="Midpointv2", command=lambda: self.redraw("Midpointv2"))
        button.pack(side=tk.BOTTOM)
        self.create_input("Radius")
        self.radius = tk.Entry(self.master, width=5)
        self.radius.pack()

    def create_input(self, name):
        label = tk.IntVar(value=20)
        label.set(name)
        label_dir = tk.Label(self.master, textvariable=label, width=10)
        label_dir.pack()

    def paint(self, event):
        p1 = Point(event.x, event.y)
        print(p1)
        self.create_dot(p1)
        if self.mode == self.DDA:
            if not self.no_points % 2:
                self.mode()
                self.i += 1
        else:
            self.mode()

    def create_dot(self, p1: Point):
        self.canvas.create_oval(p1.x, p1.y, p1.x + 1, p1.y + 1, fill=python_green)
        self.points.append(p1)

    def redraw(self, mode=None):
        self.points = []
        self.canvas.delete("all")
        if mode and mode in self.modes:
            self.mode = self.modes[mode]

    def DDA(self):
        # Pseudocode void lineDDA(int x1, int y1, int x2, int y2){float dy = y2 - y1;float dx = x2 - x1;float m = dy/dx;float y = y1;for (int x = x1; x <= x2; ++x){putPixel(x, round(y));y += m;}}
        print(f"DDA {self.i}")
        p1, p2 = arrange_points(self.points[-2:])
        dy = p2.y - p1.y
        dx = p2.x - p1.x
        m = dy / dx
        y = p1.y
        for x in range(p1.x + 1, p2.x):
            self.create_dot(Point(x, round(y)))
            y += m
        print(self.points)

    def midpoint_circle_v2(self):
        # Midpoint Circle v. 2 - addition only (s. 17) void MidpointCircle(int R) { int d = 1-R; int x = 0; int y = R; putPixel(x, y); while (y > x) { if ( d < 0 ) //move to E d += 2*x + 3; else //move to SE { d += 2*x - 2*y + 5; --y; } ++x; putPixel(x, y); } }
        p = self.points[-1]
        R = int(self.radius.get() or 0)
        dE = 3
        dSE = 5 - 2 * R
        d = 1 - R
        x = p.x
        y = p.y + R
        self.create_dot(Point(x, y))
        while y > x:
            if d < 0:
                d += dE
                dE += 2
                dSE += 2
            else:
                d += dSE
                dE += 2
                dSE += 4
                y -= 1
            x += 1
            self.create_dot(Point(x, y))

    def gupta_sproull(self):
        # Gupta-Sproull - lines with thickness (s. 22-29)
        raise NotImplementedError

    def drawing_withpen(self):
        raise NotImplementedError

    @property
    def modes(self):
        return {
            "DDA": self.DDA,
            "Midpointv2": self.midpoint_circle_v2,
            "Gupta-Sproull": self.gupta_sproull,
            "Drawing with pen": self.drawing_withpen,
        }

    @property
    def no_points(self):
        return len(self.points)


if __name__ == '__main__':
    master = tk.Tk()
    master.title("Canvas Drawing")
    w = tk.Canvas(master,
                  width=canvas_width,
                  height=canvas_height, bd=5, highlightthickness=0, relief='ridge')
    w.pack()
    b = Board(master, w)

    tk.mainloop()
