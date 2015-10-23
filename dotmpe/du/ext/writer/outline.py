"""

Last time I looked there were a lot of tastes of outline format.

The first req,. is to get nested, identified containers out.
Get the ID from the title/term.

"""
import math
import re
import roman
from optparse import Values

from docutils import nodes, writers



__docformat__ = 'reStructuredText'


class Writer(writers.Writer):

    """
    Writer for outlines
    TODO: json formatting
    """

    defaults = Values(dict(
        outline_format = 'json',
        outline_file = 'outline.json',
        element = 'definition',
        content = 'none',
    ))

    settings_spec = (
        'Outline writer',
        None,
        (
            ( "Element, grab either section (titles) or definition (terms).",
                ['--element'],
                { 'default': defaults.element, 'metavar': '[section|definition]' }),
            ( "Content, 'body' to grab any block element, 'list' to grab the first list. ",
                ['--content'],
                { 'default': defaults.content, 'metavar': '[none,body,list]' }),

            ( "Outline file, (default: %default). ",
                ['--outline'],
                { 'default': defaults.outline_file, 'dest': 'outline_file', 'metavar': '<FILE>' }),

            ( "Outline format, '%default' for now. ",
                ['--format'],
                { 'default': defaults.outline_format, 'dest': 'outline_format',
                    'metavar': '<FORMAT>' }),
        )
    )

    def __init__(self):
        writers.Writer.__init__(self)

    def init_from_settings(self):
        settings = self.document.settings
        self.outline_file = getattr(settings, 'outline_file',
                self.__class__.defaults.outline_file)
        self.outline_format = getattr(settings, 'outline_format',
                self.__class__.defaults.outline_format)
        self.element = getattr(settings, 'element',
                self.__class__.defaults.element)
        self.content = getattr(settings, 'content',
                self.__class__.defaults.content)

    def translate(self):
        self.init_from_settings()

        visitor = OutlineExtractor(self.document,
                self.element, self.content)
        self.document.walkabout(visitor)

        self.output = visitor.astext()


#class OutlineExtractor(nodes.NodeVisitor):
class OutlineExtractor(nodes.SparseNodeVisitor):

    def __init__(self, document, element, content):
        nodes.NodeVisitor.__init__(self, document)
        self.data = {}
        "Dist-n-list struct for return JSON"
        self.current_element = {}
        "Dict for current element. "
        self.previous_elements = []
        "Stack for parent elements. "
        if element == 'section':
            self.visit_section = self.continue_outline
            self.visit_title = self.capture_label
            self.visit_subtitle = self.continue_label
            self.depart_section = self.flush_outline
        elif element == 'definition':
            self.visit_definition_list_item = self.continue_outline
            self.visit_term = self.capture_label
            self.depart_definition_list_item = self.flush_outline

    def astext(self):
        return str(self.data)

    def continue_outline(self, node):

        """
        If in previous element (or root), start new outline. Otherwise
        continue where left off.
        """

        print 'start', node.tagname

        if not self.previous_elements or is_parent( self.previous_elements[-1], node ):
            self.current_element = {}
            if not self.data:
                print 'no-data'
                self.data['root'] = self.current_element
                self.data['_id'] = 'root'
                self.data['_label'] = 'Root'
                self.previous_elements = [ self.data ]

            else:
                previous = self.previous_elements[-1]
                id = previous['_id']
                #self.previous_element =
                previous[id] = self.current_element


    def capture_label(self, node):

        """
        """

        self.current_element['_label'] = node.astext()

    def continue_label(self, node):
        self.current_element['_label'] += ': '+ node.astext()


    def flush_outline(self, node):

        """
        There is nothing to add to current outline, finalize.
        """

        ce = self.current_element
        ce['_id'] = nodes.make_id(ce['_label'])
        print 'end', self.current_element, self.previous_elements


def is_parent(node1, node2):
    supnode = node2
    while supnode.parent:
        supnode = supnode.parent
        if supnode == node1:
            return True


