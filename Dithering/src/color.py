class Color:
    def __init__(self, red=0, green=0, blue=0, alpha=None):
        self.red = int(red)
        self.green = int(green)
        self.blue = int(blue)
        self.alpha = int(alpha) if alpha is not None else None

    def __str__(self):
        return f"Color: r={self.red},g={self.green},b={self.blue}"
