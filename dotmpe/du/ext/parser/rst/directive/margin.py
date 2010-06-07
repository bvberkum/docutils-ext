"""reStructuredText left/right margin directive, and doctree nodes.
python-docutils extension.

Copyleft 2009  Berend van Berkum <dev@dotmpe.com>
This file has been placed in the Public Domain.

See dotmpe.du.node.margin.
This file adds a directive to parse these nodes from reStructuredText.
"""
from docutils.parsers.rst import Directive, directives


# Directives for registration with docutils' rSt parser
class Margin(Directive):

    """
    A decorative element for contents in the side margins of a page.
    Like the header and footer decorative elements, this allows page
    contents beside the documents' body.

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



