
class Node:

    def __init__(self, edge=None, *args):
        self.edge = {}
        self.doc = []
        if edge is not None:
            self.edge.update({str(edge): Node()})
        self.doc.extend(list(args))

    def add_doc(self, *args):
        self.doc.extend(list(args))

    def add_edge(self, edge):
        self.edge.update({str(edge): Node()})


class Trie(Node):

    def __init__(self):
        self.Trie_Root = Node()

    def add_word(self, word, *args):
        current_node = self.Trie_Root
        for c in word:
            if c not in current_node.edge:
                current_node.add_edge(c)
            current_node = current_node.edge[c]

        current_node.add_doc(*args)

    def get_doc(self, word):
        current_node = self.Trie_Root
        for c in word:
            if c not in current_node.edge:
                return False

            current_node = current_node.edge[c]

        if len(current_node.doc):
            return list(current_node.doc)
        else:
            return False

