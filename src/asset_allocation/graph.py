from typing import Optional

class Graph:
    def __init__(self):
        self.nodes = {}

class Node:
    name: str
    parent: Optional['Node']
    value: float

    def __init__(self, name: str, parent: Optional['Node'] = None):
        self.name = name
        self.parent = parent

class LeafNode(Node):
    @property
    def children(self):
        return []

class InternalNode(Node):
    children: list[Node]

    def __init__(self, name: str, children: list[Node]):
        super().__init__(name)
        self.children = children

    @property
    def value(self):
        return sum(child.value for child in self.children) 