"""Parse and serialize docutils documents from and to reStructuredText.

XXX: This is a heavy work in progress.
"""
from docutils import nodes, writers


class Writer(writers.Writer):

    """
    docutils Writer that writes a doc-tree 'back' to rSt.
    """

    def __init__(self):
        writers.Writer.__init__(self)
        self.translator_class = RstTranslator

    def translate(self):
        visitor = self.translator_class(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.astext()


class RstTranslator(nodes.NodeVisitor):

    """Visit docutils tree and serialize to rSt.
    TODO: RstTranslator(nodes.NodeVisitor)
    """

    indent = '   '
    title_markers = []
    level = 0
    depth = 0

    title = ''
    docinfo = {}
    body = []
    references = []

    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        self.settings = settings = document.settings
        self.in_docinfo = None
        self.in_field_list = None
        self.in_block_quote = None
        self.in_figure = None
        self.in_image = None
        self.in_footnote = None
        self.in_enumerated_list = 0
        self.in_bullet_list = 0
        self.in_list_item = 0
        self.in_line_block = None

        self.level = 0 # count indented blocks
        self.indent = '   '
        self.depth = 0 # count section nesting 
        self.title_markers = ['=', '-', '~', '^', '+', "'"]
        self.docinfo = {}
        self.body = []
        self.references = []

    def astext(self):
        return "".join(self.body)

    def add_directive(self, name, *args):
        self.body.append("\n.. %s:: %s\n\n" % (name, ' '.join(args)))

    # NodeVisitor hooks

    def visit_document(self, node):
        pass

    def depart_document(self, node):
        pass

    def visit_Text(self, node):
        text = node.astext()
        #encoded = self.encode(text)
        #if self.in_mailto and self.settings.cloak_email_addresses:
        #    encoded = self.cloak_email(encoded)
        self.body.append(self.indent * self.level + text)
    def depart_Text(self, node):
        pass

    def visit_title(self, node):
        pass
    def depart_title(self, node):
        title = node.astext()
        self.body.append('\n' + "".rjust(len(title), self.title_markers[self.depth]) + '\n')

    def visit_subtitle(self, node):
        pass
    def depart_subtitle(self, node):
        title = node.astext()
        self.depth += 1
        self.body.append('\n' + "".rjust(len(title),
        	self.title_markers[self.depth]) + '\n')

    def visit_section(self, node):
        self.depth += 1
    def depart_section(self, node):
        self.depth += 1
        self.body.append('\n')

    def visit_title_reference(self, node):
        self.body.append('`')
    def depart_title_reference(self, node):
        self.body.append('`')

    def visit_reference(self, node):
        if self.in_figure:
            pass
        else:
            if 'refuri' in node:
                if node.astext() == node['refuri']:
                    pass
                else:
                    self.body.append('`')
            elif 'refid' in node:
                print node

    def depart_reference(self, node):
        if self.in_figure:
            self.body.append("   :target: %s\n" %node['refuri'])
        else:
            if 'refuri' in node:
                if node.astext() == node['refuri']:
                    pass
                else:
                    self.body.append('`_')
            elif 'refid' in node:
                pass

    def visit_target(self, node):
        if 'refuri' in node:
            self.body.append(".. _%s:: %s\n" % (node['ids'][0], node['refuri']))
        else:
            pass #@fixme

#    def visit_footnote(self, node):
#        self.in_footnote = 1
#        self.body.append(".. [")
#    def visit_label(self, node):
#        print node
#    def depart_label(self, node):
#        print node
#    def depart_label(self, node):
#        if self.in_footnote:
#            self.body.append("] ")
#    def depart_footnote(self, node):
#        self.body.append("\n")

    def depart_paragraph(self, node):
        if self.in_field_list or self.in_docinfo or self.in_footnote \
            or self.in_enumerated_list or self.in_bullet_list: pass
        else:
            self.body.append("\n\n")

    def visit_paragraph(self, node):
        if self.in_block_quote:
            self.body.append(' ')
        elif self.in_figure:
            self.body.append('    ')

#    def visit_block_quote(self, node):
#        # set marker, wait till depart and indent block
#        if 'classes' in node:
#            if 'epigraph' in node['classes']:
#                self.append('.. epigraph:: ')
#        else:
#            self.in_block_quote = len(self.body)
#
#    def depart_block_quote(self, node):
#        self.in_block_quote = None
#        return
#        # indent up until last marker

    def visit_transition(self, node):
        self.body.append("\n----\n\n")

    def visit_image(self, node):
        self.in_image = 1
        if self.in_figure:
            self.body.append(node['uri'] +'\n')
        else:
            self.add_directive('image', node['uri'])
    def depart_image(self, node):
        self.in_image = 0

    def visit_figure(self, node):
        self.in_figure = True
        self.body.append("\n.. figure:: ")
    def depart_figure(self, node):
        self.body.append("\n\n")
        self.in_figure = None

    def visit_caption(self, node):
        self.body.append('\n   ')
    def depart_caption(self, node):
        self.body.append('\n')

    def visit_footnote_reference(self, node):
        self.body.append('[')

    def depart_footnote_reference(self, node):
        self.body.append(']_ ')

    def visit_substitution_definition(self, node):
        self.body.append('.. |%s| ::' % node['names'][0])

    def depart_substitution_definition(self, node):
        self.body.append('\n')

    def visit_citation_reference(self, node):
        self.body.append('[')

    def depart_citation_reference(self, node):
        self.body.append(']_ ')

    def visit_emphasis(self, node):
        self.body.append('*')

    def depart_emphasis(self, node):
        self.body.append('*')

    def visit_strong(self, node):
        self.body.append('**')

    def depart_strong(self, node):
        self.body.append('**')

    def visit_literal(self, node):
        self.body.append('``')

    def depart_literal(self, node):
        self.body.append('``')

    def visit_literal_block(self, node):
        # @fixme: indent
        self.body.append('::\n')

    def visit_comment(self, node):
        self.body.append('.. ')
        self.level += 1
    def depart_comment(self, node):
        self.body.append('\n\n')
        self.level -= 1

#    def visit_attribution(self, node):
#        # @fixme: indent
#        self.body.append('---')
#    def depart_attribution(self, node):
#        self.body.append('\n')

    def visit_line_block(self, node):
        self.in_line_block = 1
    def depart_line_block(self, node):
        self.in_line_block = None
        self.body.append('\n')

    def visit_line(self, node):
        self.body.append(' | ')
    def depart_line(self, node):
        self.body.append('\n')

    # Lists
    def visit_enumerated_list(self, node):
        self.in_enumerated_list += 1

    def depart_enumerated_list(self, node):
        self.in_enumerated_list -= 1
        self.body.append('\n')

    def visit_bullet_list(self, node):
        self.in_bullet_list += 1

    def depart_bullet_list(self, node):
        self.in_bullet_list -= 1
        self.body.append('\n')

    def visit_list_item(self, node):
        self.in_list_item += 1

        # @fixme: proper nesting
        if self.in_bullet_list:
            pref = '  ' * (self.in_bullet_list-1)
            self.body.append(pref + '* ')

        elif self.in_enumerated_list:
            pref = '  ' * (self.in_enumerated_list-1)
            self.body.append(pref + '%s. ' % self.in_list_item)

    def depart_list_item(self, node):
        self.in_list_item -= 1
        self.body.append('\n')

    # Fields lists

    def visit_docinfo(self, node):
        self.in_docinfo = 1

        #nodes.author,
        #nodes.authors,
        #nodes.organization,
        #nodes.address,
        #nodes.contact,
        #nodes.version,
        #nodes.revision,
        #nodes.status,
        #nodes.date,
        #nodes.copyright,
        #'dedication':nodes.topic,
        #'abstract':nodes.topic

        # RCSfile

    def depart_docinfo(self, node):
        self.in_docinfo = None
        self.body.append('')

    def visit_author(self, node):
        self.body.append(":author: ")

    def depart_author(self, node):
        self.body.append("\n")

    def visit_field_list(self, node):
        self.in_field_list = 1

    def depart_field_list(self, node):
        self.in_field_list = None
        self.body.append('\n')

    def visit_field(self, node):
        pass

    def depart_field(self, node):
        self.body.append("\n")

    def visit_field_name(self, node):
        self.body.append(":")

    def depart_field_name(self, node):
        self.body.append(": ")

    def visit_field_body(self, node):
        pass

    def depart_field_body(self, node):
        pass

    # Tables
    def visit_entry(self, node):
        pass
    def visit_row(self, node):
        pass
    def visit_tbody(self, node):
        pass
    def visit_tgroup(self, node):
        pass
    def visit_table(self, node):
        pass
    def visit_colspec(self, node):
        pass

    def unknown_visit(self, node):
        #print "not visiting", node.__class__.__name__
        #return
        raise NotImplementedError(
            '%s visiting unknown node type: %s'
            % (self.__class__, node.__class__.__name__))

    def unknown_departure(self, node):
        #print "still open", node.__class__.__name__
        #return
        raise NotImplementedError(
            '%s departing unknown node type: %s'
            % (self.__class__, node.__class__.__name__))

    # Decoration
    def visit_decoration(self, node):
        pass
    def depart_decoration(self, node):
        pass

    def visit_header(self, node):
        self.add_directive('header')
        self.level += 1
    def depart_header(self, node):
        self.level -= 1

    def visit_footer(self, node):
        self.add_directive('footer')
        self.level += 1
    def depart_footer(self, node):
        self.level -= 1

    def visit_right_margin(self, node):
        self.add_directive('left_margin')
        self.level += 1
    def depart_right_margin(self, node):
        self.level -= 1

    def visit_left_margin(self, node):
        self.add_directive('right_margin')
        self.level += 1
    def depart_left_margin(self, node):
        self.level -= 1


if __name__ == '__main__':
    import os
    import init
    import docutils.core
    for doc in init.TEST_DOC:
        print (' ' + doc).rjust(70, '=')
        rst = open(doc).read()
        original_tree = docutils.core.publish_parts(
                source=rst, 
                writer_name='pseudoxml')['whole']#writer_name='dotmpe-rst')
        result = docutils.core.publish_parts(
                source=rst, 
                writer=Writer())['whole']#writer_name='dotmpe-rst')
        generated_tree = docutils.core.publish_parts(
                source=result,
                writer_name='pseudoxml')['whole']
        print (doc).rjust(70, '=')
        print rst.strip()
        print
        print result.strip()
        print

