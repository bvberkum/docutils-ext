"""reStructuredText left/right margin directives,
python-docutils extension.

Copyleft 2009  Berend van Berkum <dev@dotmpe.com>
This file has been placed in the Public Domain.
"""
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives


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


class Margin(Directive):

    """
    A decorative element for contents in the side margins of a page.
    Like the header and footer decorative elements, this allows page
    contents beside the documents body.

    A page can have two margings, left and right, multiple occurrences are
    merged in order.
    """

    required_arguments = 0
    optional_arguments = 1
    has_content = True
    option_spec = {'class': directives.class_option}

    def run(self):
        side_value = 'left'
        try:
            side_value = side(self.arguments[0])
        except ValueError:
            raise self.warning(
                'Invalid %s side: "%s".'
                % (self.name, self.arguments[0]))

        class_value = self.options.get('class', [])

        text = '\n'.join(self.content)
        if side_value == 'left':
            node = self.state_machine.document.get_decoration().get_left_margin()
        elif side_value == 'right':
            node = self.state_machine.document.get_decoration().get_right_margin()
        node['classes'] += class_value
        if self.content:
            self.state.nested_parse(self.content, self.content_offset, node)
        return []


