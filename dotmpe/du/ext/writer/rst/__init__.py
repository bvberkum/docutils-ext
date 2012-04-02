"""Parse and serialize docutils documents from and to reStructuredText.

XXX: This is a heavy work in progress. RstTranslator has some issues with
     inline nodes and does not do tables.

"""
import math
import re
import roman

from docutils import nodes, writers

from rstobjects import *


__docformat__ = 'reStructuredText'


class Writer(writers.Writer):

    """
    docutils Writer that writes a doc-tree 'back' to rSt.
    This implementation is lossy.
    """

    settings_spec = (
        'rST writer',
        None,
        ()
    )

    def __init__(self):
        writers.Writer.__init__(self)

    def translate(self):

        visitor = RstPreTranslator(self.document)
        self.document.walkabout(visitor)

        visitor = RstTranslator(self.document, visitor)
        self.document.walkabout(visitor)

        self.output = visitor.body


class RstPreTranslator(nodes.NodeVisitor):

    """
    Pre-pass document visitor. Accumulates indices.
    """

    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        #self.settings = document.settings
        self.id_references = {}
        self.uri_references = {}
        self.anonymous_references = {}

    def visit_reference(self, node):
        anonymous = attr(node, 'anonymous')
        classes = attr(node, 'classes')
        ref_uri = attr(node, 'refuri')
        ref_id = attr(node, 'refid')
        if ref_id:
            self.id_references[ref_id] = node
        #print node['names'], locals()

    def unknown_visit(self, node): pass
    def unknown_departure(self, node): pass


class RstTranslator(nodes.NodeVisitor):

    formatters = {
            'document': RstDocumentFormatter,
            'section': RstSectionFormatter,
            'table': RstTableFormatter,
        }

    def __init__(self, document, pretranslator, text_width=79):
        nodes.NodeVisitor.__init__(self, document)
        # fetch indices from RstPreTranslator
        for attr in 'id_references', 'uri_references', 'anonymous_references':
            setattr(self, attr, getattr(pretranslator, attr))
        self.text_width = text_width
        self.stack = ContextStack({})
        self.settings = document.settings

    def __getattr__(self, name):
        if name.startswith('visit'):
            return self.append
        elif name.startswith('depart'):
            return self.flush
        else:
            return self.__dict__[name]
        
    def append(self, node):
        if node.tagname in self.formatters:
            # initialize new (sub)formatter for this node
            formatter = self.formatters[node.tagname](node, self.settings)
            # copy over current or set new index
            if hasattr(self.stack, 'formatter') and self.stack.formatter:
                formatter.context.index = self.stack.formatter.context.index
            else:
                formatter.context.index = 0
            self.stack.formatter = formatter

        # defer to node visitor
        assert self.stack.formatter, node
        if node.tagname == '#text':
            visitor_name = 'visit_Text'
        else:
            visitor_name = 'visit_' + node.tagname
        assert hasattr(self.stack.formatter, visitor_name), visitor_name
        visitor = getattr(self.stack.formatter, visitor_name)
        visitor(node)

    def flush(self, node):
        # defer to node departor
        assert self.stack.formatter, node
        if node.tagname == '#text':
            departor_name = 'depart_Text'
        else:
            departor_name = 'depart_' + node.tagname
        assert hasattr(self.stack.formatter, departor_name), departor_name
        departor = getattr(self.stack.formatter, departor_name)
        departor(node)

        if node.tagname in self.formatters:
            # finalize current formatter
            subdoc = self.stack.formatter.flush(node)
            # pop formatter from stack, copy index to underlaying formatter
            new_index = self.stack.formatter.context.index
            del self.stack.formatter
            if hasattr(self.stack, 'formatter') and self.stack.formatter:
                del self.stack.formatter.context.index
                self.stack.formatter.context.index = new_index
            self.body = subdoc
            return subdoc

## Main/test

if __name__ == '__main__':
    import os, sys, glob

    import curses;v=curses.initscr();x=v.getmaxyx();curses.endwin();
    max_width = x[1]

    print " Test run".rjust(max_width, '_')

    sys.path.insert(0, 'test')
    util = __import__('util')

    if sys.argv[1:]:
        for doc in sys.argv[1:]:
            assert os.path.exists(doc) and doc.endswith('.rst'), doc
            util.print_compare_writer(doc, writer_class=Writer, max_width=max_width)
    else:

        p = os.path.realpath(__file__)
        for i in range(0, 5):
            p = os.path.dirname(p)
        PROJ_ROOT = p
        
        TEST_DOC = [
#            'var/test-10.literal-block-1.rst',
#            'var/test-1.document-6.rst',
#            'var/test-1.document-7.rst',
            'var/test-5.inline-1.rst',
#            'var/test-5.inline-2.rst',
#            'var/test-5.inline-3.rst',
#            'var/test-5.inline-4.rst',
#            'var/test-22.docinfo.rst',
#            'var/test-23.option-lists.rst',
#            'var/_test-1.document-5.full-rst-demo.rst'
        ]
        #TEST_DOC = filter(os.path.getsize,
        #        glob.glob(os.path.join(PROJ_ROOT, 'var', '*.rst')))
        TEST_DOC.sort()

        for doc in TEST_DOC:
            util.print_compare_writer(doc, writer_class=Writer, max_width=max_width)

