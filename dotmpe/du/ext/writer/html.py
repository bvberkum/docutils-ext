"""docutils HTML4CSS1 writer with support for left/right margins.

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

    def starttag(self, node, tagname, suffix='\n', empty=0, **attributes):
        # XXX: dont allow frame(=void) or rules(=none)
        if 'rules' in attributes:
            del attributes['rules'] 
        if 'frame' in attributes:
            del attributes['frame'] 
        return html4css1.HTMLTranslator.starttag(self, node, tagname, suffix=suffix,
                empty=empty, **attributes)

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

    def visit_system_message(self, node):
        self.body.append(self.starttag(node, 'div', 
            CLASS='system-message level-%s %s'%(node['level'],
                node['type'].lower())))
        self.body.append('<p class="system-message-title">')
        backref_text = ''
        if len(node['backrefs']):
            backrefs = node['backrefs']
            if len(backrefs) == 1:
                backref_text = ('; <em><a href="#%s">backlink</a></em>'
                                % backrefs[0])
            else:
                i = 1
                backlinks = []
                for backref in backrefs:
                    backlinks.append('<a href="#%s">%s</a>' % (backref, i))
                    i += 1
                backref_text = ('; <em>backlinks: %s</em>'
                                % ', '.join(backlinks))
        if node.hasattr('line'):
            line = ', line %s' % node['line']
        else:
            line = ''
        self.body.append('%s/%s '
                         '(<tt class="docutils">%s</tt>%s)%s</p>\n'
                         % (node['type'], node['level'],
                            self.encode(node['source']), line, backref_text))



class Writer(html4css1.Writer):

    supported = ('html', 'html4css1', )
    """Formats this writer supports."""

    visitor_attributes = \
        html4css1.Writer.visitor_attributes + \
        ( 'left_margin', 'right_margin', )

    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = HTMLTranslator

