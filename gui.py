import tkinter as tk
from PIL import ImageTk, Image
import numpy as np
from tkinter import Canvas, filedialog
import collections
from functools import partial
import itertools

canvas_width = 256
canvas_height = 256
python_green = "#476042"

filters_database = {
    'blur': np.array((
        [1 / 25, 1 / 25, 1 / 25, 1 / 25, 1 / 25],
        [1 / 25, 1 / 25, 1 / 25, 1 / 25, 1 / 25],
        [1 / 25, 1 / 25, 1 / 25, 1 / 25, 1 / 25],
        [1 / 25, 1 / 25, 1 / 25, 1 / 25, 1 / 25],
        [1 / 25, 1 / 25, 1 / 25, 1 / 25, 1 / 25],
    ), dtype="float"),
    'gaussian': np.array((
        [0, 1 / 25, 2 / 25, 1 / 25, 0],
        [1 / 25, 4 / 25, 8 / 25, 4 / 25, 1 / 25],
        [2 / 25, 8 / 25, 16 / 25, 8 / 25, 2 / 25],
        [1 / 25, 4 / 25, 8 / 25, 4 / 25, 1 / 25],
        [0, 1 / 25, 2 / 25, 1 / 25, 0]), dtype="float"),
    'sharpen1': np.array((
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]), dtype="int"),
    'sharpen2': np.array((
        [-1, -1, -1],
        [-1, 9, -1],
        [-1, -1, -1]), dtype="int"),
    'Hedgedetect(set offset=127)': np.array((
        [0, -1, 0],
        [0, 1, 0],
        [0, 0, 0]), dtype="int"),
    'Vedgedetect(set offset=127)': np.array((
        [0, 0, 0],
        [-1, 1, 0],
        [0, 0, 0]), dtype="int"),
    'Dedgedetect(set offset=127)': np.array((
        [-1, 0, 0],
        [0, 1, 0],
        [0, 0, 0]), dtype="int"),
    'laplacian1': np.array((
        [0, -1, 0],
        [-1, 4, -1],
        [0, -1, 0]), dtype="int"),
    'laplacian2': np.array((
        [-1, -1, -1],
        [-1, 8, -1],
        [-1, -1, -1]), dtype="int"),
}


class WindowInter:
    entries = []
    top, bottom, mode, kernel_choice = None, None, None, None
    offset, divisor = None, None
    contrast, brightness = None, None
    k_height, k_width, anchor_row, anchor_col = None, None, None, None

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Computer Graphics 1")
        self.window.geometry("600x600")
        self.window.configure(background='grey')
        self.panel3 = tk.Label(self.window)
        self.panel3.pack(side="left")
        self.points = {}

    def button_filter_handler(self, key):
        middle = int((len(filters_database[key][0]) - 1) / 2)
        (self.anchor_col, self.anchor_row) = (middle, middle)
        (self.k_width, self.k_height) = filters_database[key].shape
        filts = filters_database[key].flatten()
        for index, entry in enumerate(self.entries):
            entry.insert(1, str(filts[index]))
        self.show_images(filters_database[key])

    def function_filters_handler(self, method):
        window = tk.Tk()
        window.title("Computer Graphics 1")
        window.geometry("800x800")
        window.configure(background='grey')
        raw = self.top.copy()
        raw = to_tkimage(raw)
        filtered = to_tkimage(method())
        tkimg1 = ImageTk.PhotoImage(raw, master=window)
        tkimg2 = ImageTk.PhotoImage(filtered, master=window)
        panel1 = tk.Label(window, image=tkimg1)
        panel2 = tk.Label(window, image=tkimg2)
        panel1.pack(side="top", fill="both", expand="yes")
        panel2.pack(side="bottom", fill="both", expand="yes")
        window.mainloop()

    def create_function_filters_buttons(self):
        panel5 = tk.Label(self.window)

        command_with_arg = partial(self.function_filters_handler, self.set_contrast)
        button = tk.Button(panel5, text="Contrast", command=command_with_arg)
        button.pack()

        command_with_arg = partial(self.function_filters_handler, self.set_brightness)
        button = tk.Button(panel5, text="Brightness", command=command_with_arg)
        button.pack()

        command_with_arg = partial(self.function_filters_handler, self.inversion)
        button = tk.Button(panel5, text="Inversion", command=command_with_arg)
        button.pack()
        panel5.pack(side='bottom')

    def create_readymade_filter_buttons(self):
        panel5 = tk.Label(self.window)
        for key in filters_database:
            command_with_arg = partial(self.button_filter_handler, key)
            button = tk.Button(panel5, text=key, command=command_with_arg)
            button.pack()
        panel5.pack(side='right')

    def create_input(self, name):
        label = tk.StringVar()
        label.set(name)
        label_dir = tk.Label(self.window, textvariable=label, width=10)
        label_dir.pack()

    def show_buttons(self):
        self.create_readymade_filter_buttons()
        self.create_function_filters_buttons()
        load_image = tk.Button(self.window, text="Change Image", command=self.load_image, width=10, height=2, padx=20,
                               pady=20)
        load_image.pack()
        self.create_input("Offset")
        self.offset = tk.Entry(self.window, width=5)
        self.offset.pack()
        self.create_input("Divisor")
        self.divisor = tk.Entry(self.window, width=5)
        self.divisor.pack()
        self.create_input("Contrast")
        self.contrast = tk.Entry(self.window, width=5)
        self.contrast.pack()
        self.create_input("Brightness")
        self.brightness = tk.Entry(self.window, width=5)
        self.brightness.pack()

        self.create_left_panel()

    def load_image(self):
        fname = filedialog.askopenfilename(initialdir='.')
        raw = resize_image(Image.open(fname))
        grayscale = np.asarray(raw)[:, :, 0]
        self.top = grayscale

    def create_left_panel(self):
        panel4 = tk.Label(self.window)

        w = Canvas(panel4, width=canvas_width, height=canvas_height)
        w.pack()
        self.create_dot(0, 255, 1, 256, w)
        self.create_dot(255, 0, 256, 1, w)
        self.create_lines_between_dots(w)
        paint_with_canvas = partial(self.paint, w)
        w.bind("<B1-Motion>", paint_with_canvas)

        button = tk.Button(panel4, text="Inverse", command=lambda: self.canvas_inverse(w))
        button.pack()

        command_with_arg = partial(self.function_filters_handler, self.apply_canvas)
        button = tk.Button(panel4, text="Apply canvas", command=command_with_arg)
        button.pack()
        panel4.pack(side="left")

    def canvas_inverse(self, canvas):
        self.points = {}
        self.create_dot(0, 0, 1, 1, canvas)
        self.create_dot(255, 255, 256, 256, canvas)
        self.redraw(canvas)

    def paint(self, canvas, event):
        x1, y1 = (event.x - 1), (event.y - 1)
        x2, y2 = (event.x + 1), (event.y + 1)
        self.create_dot(x1, y1, x2, y2, canvas)
        self.redraw(canvas)

    def create_dot(self, x1, y1, x2, y2, canvas):
        canvas.create_line(x1, y1, x2, y2, fill=python_green)
        self.points[x1] = y1

    def create_lines_between_dots(self, canvas):
        sorted_points = collections.OrderedDict(sorted(self.points.items()))
        for p1, p2 in zip(list(sorted_points), list(sorted_points)[1:]):
            canvas.create_line(p1, self.points[p1], p2, self.points[p2])

    def redraw(self, canvas):
        canvas.delete("all")
        for px, py in self.points.items():
            self.create_dot(px, py, px + 1, py + 1, canvas)
        self.create_lines_between_dots(canvas)

    def calculate_real_values(self):
        """Takes points and calculate value for each point"""
        real_values = {}
        sorted_points = collections.OrderedDict(sorted(self.points.items()))
        for p1, p2 in zip(list(sorted_points), list(sorted_points)[1:]):
            slope = (self.points[p2] - self.points[p1]) / (p2 - p1)
            current_value = self.points[p1]
            for i in range(p2 - p1 + 1):
                real_values[p1 + i] = current_value
                current_value += slope
        return real_values

    def apply_canvas(self):
        real_values = self.calculate_real_values()
        img = self.top.copy()
        for i, j in itertools.product(range(img.shape[0]), range(img.shape[1])):
            img[i, j] = 255 - real_values[img[i, j]]
        return img

    def set_brightness(self):
        img = self.top.copy()
        brightness = int(self.brightness.get() or 0)
        for i, j in itertools.product(range(img.shape[0]), range(img.shape[1])):
            img[i, j] = min(255, img[i, j] + brightness)
        return img

    def inversion(self):
        img = self.top.copy()
        return 255 - img

    def set_contrast(self):
        img = self.top.copy()
        contrast = int(self.contrast.get() or 0)
        F = (259 * (contrast + 255)) / (255 * (259 - contrast))
        for i, j in itertools.product(range(img.shape[0]), range(img.shape[1])):
            img[i, j] = max(0, min(255, 128 + (F * (img[i, j] - 128))))
        return img

    def show_tk_image(self, top):
        self.top = top
        self.show_buttons()
        self.window.mainloop()

    def show_images(self, kernel):
        window = tk.Tk()
        window.title("Computer Graphics 1")
        window.geometry("600x400")
        window.configure(background='grey')

        offset = int(self.offset.get() or 0)
        divisor = int(self.divisor.get() or 1)
        anchor = (self.anchor_col, self.anchor_row)

        filtered = convolution(self.top, kernel, offset, divisor, anchor)
        raw = to_tkimage(self.top)
        filtered = to_tkimage(filtered)

        tkimg1 = ImageTk.PhotoImage(raw, master=window)
        tkimg2 = ImageTk.PhotoImage(filtered, master=window)
        panel1 = tk.Label(window, image=tkimg1)
        panel2 = tk.Label(window, image=tkimg2)
        panel1.pack(side="top", fill="both", expand="yes")
        panel2.pack(side="bottom", fill="both", expand="yes")
        window.mainloop()

    def button(self):
        input_numbers = [int(entry.get() or 0) for entry in self.entries]
        arr = np.array(input_numbers)
        arr = arr.reshape((self.k_height, self.k_width))
        self.show_images(arr)


def convolution(image, filter, offset, divisor, anchor=None):
    height, width = filter.shape
    filter = filter.flatten()
    new_image = []
    print(f'Applying filter {filter}')
    for index, rows in enumerate(zip(*[image[i:] for i in range(height)])):
        new_image.append([])
        for frame in zip(*itertools.chain(*[[row[i:] for i in range(width)] for row in rows])):
            new_pixel = max(0, min(255, offset + (np.dot(frame, filter) / divisor)))
            new_image[index].append(new_pixel)
    return np.array(new_image)


def resize_image(img):
    wpercent = (300 / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((300, hsize), Image.ANTIALIAS)
    return img


def to_tkimage(img):
    return Image.fromarray(np.uint8(img))


def main():
    path = "friend.jpg"
    raw = resize_image(Image.open(path))
    img = np.asarray(raw)
    img.setflags(write=True)
    grayscale = img[:, :, 0]
    tkobj = WindowInter()
    tkobj.show_tk_image(grayscale)


main()
