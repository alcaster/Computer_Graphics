from enum import Enum

import tkinter as tk
import numpy as np

canvas_width = 600
canvas_height = 600
python_green = "#476042"


class Board:
    def __init__(self, master, canvas):
        self.MODES = Enum('Modes', 'line')
        self.canvas = canvas
        self.master = master
        self.mode = None

        canvas.bind("<Button-1>", self.paint)
        self.make_buttons()

    def make_buttons(self):
        button = tk.Button(master, text="Line", command=lambda :self.redraw(self.MODES.line))
        button.pack(side=tk.BOTTOM)

    def paint(self, event):
        x1, y1 = (event.x - 1), (event.y - 1)
        x2, y2 = (event.x + 1), (event.y + 1)
        self.create_dot(x1, y1, x2, y2)

    def create_dot(self, x1, y1, x2, y2):
        self.canvas.create_line(x1, y1, x2, y2, fill=python_green)

    def redraw(self, mode=None):
        self.canvas.delete("all")
        self.mode = mode


if __name__ == '__main__':
    master = tk.Tk()
    master.title("Canvas Drawing")
    w = tk.Canvas(master,
                  width=canvas_width,
                  height=canvas_height, bd=5, highlightthickness=0, relief='ridge')
    w.pack()
    b = Board(master, w)

    tk.mainloop()
