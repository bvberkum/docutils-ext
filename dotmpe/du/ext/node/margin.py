"""reStructuredText left/right margin directive, and doctree nodes.
python-docutils extension.

Copyleft 2009  Berend van Berkum <dev@dotmpe.com>
This file has been placed in the Public Domain.

This file adds two nodes types to the docutils document tree
and a directive to parse these nodes from reStructuredText.
"""
from docutils import nodes


class left_margin(nodes.Decorative, nodes.Element): pass
class right_margin(nodes.Decorative, nodes.Element): pass

def side(argument):
    if argument and argument not in ('left', 'right'):
        raise ValueError('side argument must be "left" or "right", not: %s\n' % argument)
    return argument

# Override docutils.node.decoration
class decoration(nodes.decoration):

    """
    The decoration node starts with a header and ends with a footer.
    In between may be two margins, one left and one right.
    """

    def get_left_margin(self):
        for child in self.children:
            if isinstance(child, left_margin):
                return child
        node = left_margin()
        self.append(node)
        return node

    def get_right_margin(self):
        for child in self.children:
            if isinstance(child, right_margin):
                return child
        node = right_margin()
        self.append(node)
        return node

nodes.decoration = decoration

