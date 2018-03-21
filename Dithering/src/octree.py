from src.color import Color


class OctreeQuantizer:

    def __init__(self, max_depth=8):
        self.max_depth = max_depth
        self.levels = {i: [] for i in range(self.max_depth)}
        self.root = OctreeNode(0, self)


class OctreeNode:

    def __init__(self, level, parent):
        self.color = Color(0, 0, 0)
        self.pixel_count = 0
        self.palette_index = 0
        self.children = [None for _ in range(8)]
        # add node to current level
        if level < OctreeQuantizer.MAX_DEPTH - 1:
            parent.add_level_node(level, self)
