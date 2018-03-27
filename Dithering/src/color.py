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
