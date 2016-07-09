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
from dotmpe.du.ext.writer.rst import ContextStack


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

        self.context = ContextStack(defaults={
            'path': [],
            'element': None
        })


    def astext(self):
        return str(self.data)

    def visit_definition_list_item(self, node):

        """
        """

        # pylint: disable=no-member
        self.context.path += [node]
        # pylint: enable=no-member

    def visit_term(self, node):

        """
        """

    def depart_term(self, node):

        self.context.element['_label'] = node.astext()
        print 'term end', node.astext(), self.context.element


    def depart_definition_list_item(self, node):

        """
        If there was a sub-dl in the item, then now there is nothing to add to
        it. We don't care about content otherwise.
        Finalize by copying the current outline path to data.
        """

        # pylint: disable=no-member
        ce = self.context.element
        # pylint: disable=no-member

        ce['_id'] = nodes.make_id(ce['_label'])

        print 'end', ce, self.context.path

        # pylint: disable=no-member
        if is_parent( self.context.path[-1], node ):
            del self.context.path
        # pylint: disable=no-member


def is_parent(node1, node2):
    supnode = node2
    while supnode.parent:
        supnode = supnode.parent
        if supnode == node1:
            return True


