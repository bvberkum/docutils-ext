
class RstObject(object):
    """
    Serializer helpers for docutils rST format.
    """

    def __init__(self, node):
        self.node = node

class RstDocument(RstObject):
    pass

class RstTitle(RstObject):
    pass


