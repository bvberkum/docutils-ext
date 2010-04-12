"""docutils xhtmlwriter with support for left/right margins.

Copyleft 2009  Berend van Berkum <dev@dotmpe.com>
This file has been placed in the Public Domain.
"""
from docutils import nodes
from docutils.writers import html4css1


class HTMLTranslator(html4css1.HTMLTranslator):

    def __init__(self, document):
        html4css1.HTMLTranslator.__init__(self, document)
        self.left_margin = []
        self.right_margin = []

    def visit_left_margin(self, node):
        self.context.append(len(self.body))

    def depart_left_margin(self, node):
        start = self.context.pop()
        margin = [self.starttag(node, 'div', CLASS='margin left')]
        margin.extend(self.body[start:])
        margin.append('</div>')
        self.body_prefix = \
            self.body_prefix[:1] + margin + self.body_prefix[1:]
        self.left_margin.extend(margin)
        del self.body[start:]

    def visit_right_margin(self, node):
        self.context.append(len(self.body))

    def depart_right_margin(self, node):
        start = self.context.pop()
        margin = [self.starttag(node, 'div', CLASS='margin right')]
        margin.extend(self.body[start:])
        margin.append('</div>')
        self.body_prefix =  \
            self.body_prefix[:1] + margin + self.body_prefix[1:]
        self.right_margin.extend(margin)
        del self.body[start:]


class Writer(html4css1.Writer):

    visitor_attributes = \
        html4css1.Writer.visitor_attributes + \
        ( 'left_margin', 'right_margin', )

    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = HTMLTranslator

