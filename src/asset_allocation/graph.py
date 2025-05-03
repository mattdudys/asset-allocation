from typing import Optional

class Node:
    name: str
    parent: Optional['Node']
    children: list['Node']

    def __init__(self, name: str, children: list['Node'] = None):
        self.name = name
        self.parent = None
        self.children = children or []

    @property
    def value(self):
        if not self.children:
            return 0.0
        return sum(child.value for child in self.children) 