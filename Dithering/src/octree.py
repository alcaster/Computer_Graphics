import numpy as np


class OctreeNode:
    def __init__(self, depth, parent):
        self.MAX_DEPTH = 8
        self.pixels_count = 0
        self.color = np.array((0, 0, 0))
        self.children = 8 * [None]
        self.parent = parent
        self.depth = depth
        self.new_color = (0, 0, 0)

    @property
    def is_leaf(self):
        return self.pixels_count > 0

    def get_leafs(self):
        leafs = []
        for i in range(len(self.children)):
            if self.children[i]:
                if self.children[i].is_leaf:
                    leafs.append(self.children[i])
                else:
                    leafs.extend(self.children[i].get_leafs())
        return leafs

    def insert(self, color, depth):
        if depth == self.MAX_DEPTH or self.is_leaf:
            self.color += color
            self.pixels_count += 1
            return self.pixels_count == 1
        else:
            index = self.get_index_at_depth(color, depth)
            if not self.children[index]:
                self.children[index] = OctreeNode(depth, self)
            return self.children[index].insert(color, depth + 1)

    def find_leaf_for_color(self, color, depth):
        if self.is_leaf:
            return self
        return self.children[self.get_index_at_depth(color, depth)].find_leaf_for_color(color, depth + 1)

    def reduce_node(self):
        removed = 0
        for i in range(8):
            child = self.children[i]
            if child:
                self.color += child.color
                self.pixels_count += child.pixels_count
                removed += 1
        self.children = []
        return removed - 1

    def normalize_color(self):
        self.new_color = self.color // self.pixels_count

    @staticmethod
    def get_index_at_depth(color, depth):
        index = 0
        depth_mask = 128 >> depth
        if color[0] & depth_mask:
            index |= 1
        if color[1] & depth_mask:
            index |= 2
        if color[2] & depth_mask:
            index |= 4
        return index
