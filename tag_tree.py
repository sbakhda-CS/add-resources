
class Tree:
    def __init__(self, root):
        self.root = root

    def add_child(self, child):
        root.add_child(child)


class Node:
    def __init__(self, rss_type, key, val, parent=None, children=None):
        self.key = key
        self.val = val
        self.rss_type = rss_type
        self.parent = parent
        self.children = children

    def get_path(self):
        return

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)

    def __str__(self):
        return self.key

a = Node('agent','a','text a')
b = Node('agent','b','text b')

x = Node('x','text x',[a,b])


root = Node('root','root','Root')
tree = Tree(root)

root.add_child(a,b)



print(x)