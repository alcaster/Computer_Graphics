from collections import deque
from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.ttk import *


# from PIL import Image, ImageTk
import numpy as np

from utils.dataclasses import Point


class App(Frame):

    def __init__(self, parent):
        super(App, self).__init__()

        self.master.state('normal')
        self.master.title("Graphics")
        self.master.rowconfigure(4, weight=1)
        self.master.columnconfigure(4, weight=1)
        self.grid(sticky=W + E + N + S)

        self.parent = parent

        self.button = Button(self, text="Choose image", command=self.load_file, width=30)
        self.button.grid(row=0, column=0, sticky=W)

        self.img = None

        self.points = []

        btn_fill = Button(self, text="do it",
                          command=self.do_it)
        btn_fill.grid(row=0, column=1)

    def do_it(self):
        points = self.points


        border_pixel = points[0]
        color_point = points[1]
        start = points[2]

        border_color = self.img.get(border_pixel[0], border_pixel[1])
        color = self.img.get(color_point[0], color_point[1])
        new_color_hex = "#%02x%02x%02x" % tuple(color)

        queue = deque()
        canvas_width, canvas_height = 800, 600
        used = np.zeros((canvas_width, canvas_height))
        queue.append(Point(start[0],start[1]))
        while queue:
            pkt = queue.pop()
            pkt_color = self.img.get(pkt.x, pkt.y)
            if pkt_color != border_color:
                self.img.put(new_color_hex, (pkt.x, pkt.y))
            else:
                continue
            used[pkt.x, pkt.y] = 1
            if pkt.x + 1 < canvas_width and used[pkt.x + 1, pkt.y] == 0:
                queue.append(Point(pkt.x + 1, pkt.y))
            if pkt.x - 1 >= 0 and used[pkt.x - 1, pkt.y] == 0:
                queue.append(Point(pkt.x - 1, pkt.y))
            if pkt.y + 1 < canvas_height and used[pkt.x, pkt.y + 1] == 0:
                queue.append(Point(pkt.x, pkt.y + 1))
            if pkt.y - 1 >= 0 and used[pkt.x, pkt.y - 1] == 0:
                queue.append(Point(pkt.x, pkt.y - 1))


    def on_mouse_press(self, event):
        print(event.x, event.y)
        print(self.img.get(event.x, event.y))
        self.points.append([event.x, event.y])

    def load_file(self):
        fname = filedialog.askopenfilename(initialdir='.')
        canvas_width, canvas_height = 800, 600

        self.img = PhotoImage(file=fname)

        canvas = Label(self.parent, image=self.img)
        canvas.grid(row=1, column=0)
        canvas.bind("<ButtonPress-1>", self.on_mouse_press)


root = Tk()
app = App(root)
root.mainloop()
