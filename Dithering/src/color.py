class Color:
    def __init__(self, red=0, green=0, blue=0):
        self.red = int(red)
        self.green = int(green)
        self.blue = int(blue)

    def __str__(self):
        return f"Color: r={self.red},g={self.green},b={self.blue}"

    def __iadd__(self, other):
        self.red += other.red
        self.green += other.green
        self.blue += other.blue
        return self

    def __idiv__(self, other):
        if other is int or other is float:
            self.red = int(self.red / other.red)
            self.green /= int(self.green / other.green)
            self.blue /= int(self.blue / other.blue)
            return self
        else:
            raise Exception("This operation is not defined")

    def __truediv__(self, other):
        if other is int or other is float:
            return Color(int(self.red / other.red), int(self.green / other.green), int(self.blue / other.blue))
