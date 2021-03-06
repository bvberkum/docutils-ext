"""

Last time I looked there were a lot of tastes of outline format.

The first req,. is to get nested, identified containers out.
Get the ID from the titles or term in the document.

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
        #outline_format = 'json',
        outline_file = None
        #element = 'definition',
        #content = 'none',
    ))

    settings_spec = (
        'Outline writer',
        None,
        (
            #( "Element, grab either section (titles) or definition (terms).",
            #    ['--element'],
            #    { 'default': defaults.element, 'metavar': '[section|definition]' }),
            #( "Content, 'body' to grab any block element, 'list' to grab the first list. ",
            #    ['--content'],
            #    { 'default': defaults.content, 'metavar': '[none,body,list]' }),

            ( "Outline file, (default: %default). ",
                ['--outline'],
                { 'default': defaults.outline_file, 'dest': 'outline_file', 'metavar': '<FILE>' }),

            #( "Outline format, '%default' for now. ",
            #    ['--format'],
            #    { 'default': defaults.outline_format, 'dest': 'outline_format',
            #        'metavar': '<FORMAT>' }),
        )
    )

    def __init__(self):
        writers.Writer.__init__(self)

    def init_from_settings(self):
        settings = self.document.settings
        self.outline_file = getattr(settings, 'outline_file',
                self.__class__.defaults.outline_file)
        #self.element = getattr(settings, 'element',
        #        self.__class__.defaults.element)
        #self.content = getattr(settings, 'content',
        #        self.__class__.defaults.content)

    def translate(self):
        self.init_from_settings()

        visitor = OutlineExtractor(self.document)#, self.element, self.content)
        self.document.walkabout(visitor)

        self.data = visitor.data

        import json
        self.output = json.dumps(visitor.data)
        if self.outline_file:
            open(self.outline_file, 'w+').write(self.output)


#class OutlineExtractor(nodes.NodeVisitor):
class OutlineExtractor(nodes.SparseNodeVisitor):

    def __init__(self, document):#, element, content):
        nodes.NodeVisitor.__init__(self, document)
        self.data = { 'names': {} }
        "Dist-n-list struct for return JSON"

        # Initialize root context
        self.context = ContextStack(defaults={
            'data': self.data,
            'terms': {},
            'path': [ document ],
            'element': {},
            'outline_id': 'root'
        })


    def pretty_ctx_path(self):
        return "/".join([ p.tagname for p in self.context.path])

    def pretty_path(self, node):
        path = []
        n = node
        while n.parent:
            path.append( n.parent )
            n = n.parent


    def astext(self):
        return self.data

    def onpath(self, node):
        return is_parent( self.context.path[-1], node ) or False


    def visit_definition_list_item(self, node):
        #print 'visit-dl-li', node.line, node
        self.context.path = self.context.path + [ node ]
        self.context.terms = {}
        self.context.data = {
                'names': {}
            }

    def visit_term(self, node):
        #print 'visit-dt', node.line, node
        ce = {
                # FIXME: '_line': node.line always last line in dl tree?
                '_label': node.astext()
            }
        ce['_id'] = nodes.make_id(ce['_label'])
        self.context.element = ce

    def depart_term(self, node):
        ce = self.context.element
        del self.context.element
        self.context.outline_id = ce['_id']
        self.context.terms[ce['_id']] = ce

    def depart_definition_list_item(self, node):

        """
        If there was a sub-dl in the item, then now there is nothing to add to
        it. We don't care about content otherwise.
        Finalize by copying the current outline path to data.
        """

        data = self.context.data
        del self.context.data
        data.update( self.context.terms[ self.context.outline_id ] )
        del self.context.terms
        self.context.data['names'][self.context.outline_id] = data

        del self.context.path
        del self.context.outline_id


    def visit_definition(self, node):
        assert not node.line, "Always None?"
        #print 'visit-dd', node.line, node

        pass

    def visit_section(self, node):
        #print 'visit-section', node.line, node

        pass

    def visit_paragraph(self, node):
        #print 'visit-p', node.line, node

        pass

    def depart_definition(self, node):

        pass


def is_parent(node1, node2):
    supnode = node2
    while supnode.parent:
        supnode = supnode.parent
        if supnode == node1:
            return True


