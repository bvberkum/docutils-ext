"""Parse and serialize docutils documents from and to reStructuredText.

XXX: This is a heavy work in progress.

- I don't think rawsource should be used, however convenient.
  
"""
import re
import roman

from docutils import nodes, writers



__docformat__ = 'reStructuredText'


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


section_adornments = ['=', '-', '~', '^', '+', "\"", "'"]

class RstTranslator(nodes.NodeVisitor):

    """Visit docutils tree and serialize to rSt.
    TODO: RstTranslator(nodes.NodeVisitor)
    """

    context = None
    debug = False
    #debug_indent = True
    debug_indent = False

    indented = 0
    "The offset already indented by the current line (substract from context.indent). "

    section_adornments = []
    "The sequence of section adornments. "

    enumeration_symbol = {
        'arabic': lambda i: str(i),            
        'loweralpha': lambda i: chr(i+ord('a')-1),
        'upperalpha': lambda i: chr(i+ord('A')-1),
        'upperroman': lambda i: roman.toRoman(i).upper(),
        'lowerroman': lambda i: roman.toRoman(i).lower(),
    }
    "Map to symbol generators"

    capture_text = None
    "Concatenate Text nodes onto `key` on context. "

    #depth = 0
    #"The section level. "

    body = []
    "The list of document strings, concatenated to final file. "
    #docinfo = {}
    #references = []

    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        self.settings = settings = document.settings
        self.in_docinfo = None
        self.in_field_list = 0
        self.block_level = True
        self.in_block_quote = 0
        self.in_figure = None
        self.in_image = None
        self.in_footnote = None
        self.in_enumerated_list = 0
        self.in_bullet_list = 0
        self.in_line_block = None
        self.capture_text = None
        self.section_adornments = section_adornments        
        #self.depth = 0 # count section nesting 
        #self.docinfo = {}
        self.body = []
        #self.references = []
        self.context = ContextStack(defaults={
                'bullet': u'',
                'indent': u'',
                'section_adornment': self.section_adornments[0],
                'enumtype': u'',
                'title': None,
                'subtitle': None,
                'index': None,
                'block': None,
            })

    def astext(self):
        return "".join(self.body)

        # TODO: handle all that support the class option, and others
        #classes = node.attributes['classes']
        #if classes:
        #    self.add_directive('class',*classes)

    def add_indented(self, *lines):
        """
        Write one or more lines. The indent on the context is used to prefix the
        text. 
        The 'indented' variable indicates the lenght the current line is padded.

        FIXME: this looks wrong but I know this was behaving as expected for
        def-lists
        """
        _lines = list(lines)
        indent = self.context.indent
        while _lines:
            # write line from indent and text
            text = _lines.pop(0)
            cindent = len(text)
            self.debugprint_indent()
            if self.indented:
                # indent already satisfied
                if len(indent) <= self.indented:
                    self.body.append(text)
                # not at required indent level yet 
                else:
                    cindent += len(indent)
                    self.body.append(indent[self.indented:] + text)
            else:
                cindent += len(indent)
                self.body.append(indent + text)
            if _lines:
                self.assure_newline()
            else:
                self.indented += cindent

    def add_directive(self, name, *args):
        self.add_indented(
                u".. %s:: %s" % (name, ' '.join(args)))

    def debugprint_indent(self):                        
        if self.debug or self.debug_indent:
            if self.indented:
                self.body.append("(%i/%i)" % (self.indented,
                    len(self.context.indent)))
            else:
                self.body.append("(%i)" % 
                    len(self.context.indent))

    def add_newline(self):
        self.body.append('\n') # XXX: unix
        self.indented = 0

    @property
    def current_whitespace(self):
        "The bodies' trailing whitespace. "
        if not self.body:
            return
        idx = 0
        ws = ''
        while idx <= len(self.body):
            str_part = self.body[-idx]
            idx += 1
            ws += get_trailing_ws(str_part)
            if not is_all_ws(str_part):
                return ws

    def assure_newline(self):
        if not self.body:
            return
        ws = self.current_whitespace
        newlines = re.sub(r'[^\n]', '', ws) # XXX: unix
        if len(newlines) < 1:
            self.add_newline()

    def assure_newblock(self):
        if not self.body:
            return
        #if (self.block_level and self.context.index == 0) or not \
        #        self.block_level:
        #    return
        ws = self.current_whitespace
        newlines = re.sub(r'[^\n]', '', ws) # XXX: unix
        if len(newlines) < 2:
            self.add_newline()
        if len(newlines) < 1:
            self.add_newline()

#    @property
#    def in_container(self):
#        """
#        Wether body currently is not at an inline state, and new blocks may be
#        added with current indented/context.indent values.
#        """
#        return \
#                self.in_bullet_list or \
#                self.in_enumerated_list 
#                self.in_block_quote or \
#                self.in_topic or \
#                self.in_literal_block or \

    def increment_index(self):
        idx = self.context.index + 1
        del self.context.index
        self.context.index = idx

    def passvisit(self, node): pass

    # NodeVisitor hooks

    def visit_document(self, node):
        self.context.index = 0

    def depart_document(self, node):
        del self.context.index

    def visit_Text(self, node):
        text = node.astext()
        #encoded = self.encode(text)
        #if self.in_mailto and self.settings.cloak_email_addresses:
        #    encoded = self.cloak_email(encoded)
        if self.capture_text:
            captured = getattr(self.context, self.capture_text, '')
            setattr(self.context, self.capture_text, text)
        lines = text.split('\n') # XXX: unix
        self.add_indented(*lines)

    def depart_Text(self, node):
        pass

    def visit_title(self, node):
        self.capture_text = 'title'
    def depart_title(self, node):
        self.capture_text = None
        text = self.context.title
        self.assure_newline()
        self.add_indented( 
                            self.context.section_adornment * len(text))
        self.assure_newline()
        del self.context.title

    def visit_subtitle(self, node):
        self.capture_text = 'subtitle'
    def depart_subtitle(self, node):
        self.capture_text = None
        text = self.context.subtitle
        self.assure_newline()
        seca = self.context.section_adornment
        subindex = self.section_adornments.index(seca) + 2
        self.add_indented(self.section_adornments[subindex] * len(text))
        self.assure_newline()
        del self.context.subtitle

    def visit_section(self, node):
        self.increment_index()
        self.context.index = 0
        newlevel = self.context.depth('index')
        self.context.section_adornment = self.section_adornments[newlevel]
        self.assure_newblock()
    def depart_section(self, node):
        #self.depth += 1
        self.assure_newline()
        del self.context.index
        del self.context.section_adornment

    def visit_paragraph(self, node):
        #print self.block_level, self.context.index, node
        if self.block_level and self.context.index:
            self.assure_newblock()
        self.increment_index()
        self.context.index = 0            
        pass
        #print dir(node)
        #source = node.rawsource
        #try:
        #    parentsource = self.context.parentrawsource
        #    #print '\n%r\n%r\n%r\n' % (parentsource, source, self.rawsourceindex)
        #    newindex = parentsource.index(source, self.rawsourceindex)
        #    endsourceindex = newindex + len(source)
        #    source = parentsource[self.rawsourceindex:endsourceindex]
        #    self.rawsourceindex = endsourceindex
        #except AttributeError:
        #    pass
        #self.body.append(self.indentstring(source) + '\n')
        #raise nodes.SkipChildren
        self.block_level = False

    def depart_paragraph(self, node):
        #self.assure_newline()
        #if self.in_field_list or self.in_docinfo or self.in_footnote \
        #    or self.in_enumerated_list or self.in_bullet_list: pass
        #else:
        #    self.body.append("\n\n")
        del self.context.index
        self.block_level = True

    # Inline
    def visit_inline(self, node):
        self.increment_index()
        self.body.append('`')
    def depart_inline(self, node):
        self.body.append('`')

    def visit_emphasis(self, node):
        self.increment_index()
        self.body.append('*')
    def depart_emphasis(self, node):
        self.body.append('*')

    def visit_strong(self, node):
        self.increment_index()
        self.body.append('**')
    def depart_strong(self, node):
        self.body.append('**')

    def visit_literal(self, node):
        self.increment_index()
        self.body.append('``')
    def depart_literal(self, node):
        self.body.append('``')

    visit_subscript = passvisit
    depart_subscript = passvisit

    visit_superscript = passvisit
    depart_superscript = passvisit

    visit_classifier = passvisit
    depart_classifier = passvisit

    visit_attribution = passvisit
    depart_attribution = passvisit

    visit_description = passvisit
    depart_description = passvisit

    visit_doctest_block = passvisit
    depart_doctest_block = passvisit

    # Option lists
    visit_option_list = passvisit
    depart_option_list = passvisit

    visit_option_list_item = passvisit
    depart_option_list_item = passvisit

    visit_option_group = passvisit
    depart_option_group = passvisit

    visit_option_string = passvisit
    depart_option_string = passvisit

    visit_option = passvisit
    depart_option = passvisit

    visit_option_argument = passvisit
    depart_option_argument = passvisit

    # References
    def visit_reference(self, node):
        self.increment_index()
        if self.in_figure:
            pass
        else:
            if 'refuri' in node:
                if node.astext() == node['refuri']:
                    pass
                else:
                    self.body.append('`')
            elif 'refid' in node:
                self.debugprint(node)
    def depart_reference(self, node):
        self.increment_index()
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

    def visit_footnote_reference(self, node):
        self.increment_index()
        self.body.append('[')
    def depart_footnote_reference(self, node):
        self.body.append(']_ ')

    def visit_substitution_definition(self, node):
        self.increment_index()
        self.body.append('.. |%s| ::' % node['names'][0])
    def depart_substitution_definition(self, node):
        self.body.append('\n')

    def visit_citation_reference(self, node):
        self.increment_index()
        self.body.append('[')
    def depart_citation_reference(self, node):
        self.body.append(']_ ')

    def visit_target(self, node):
        self.increment_index()
        self.body.append(u'\n\n%s\n\n' % node.rawsource)
        #if 'refuri' in node:
        #    self.body.append(".. _%s:: %s\n" % (node['ids'][0], node['refuri']))
        #else:
        #    pass #@fixme
        self.body.append(u'\n\n%s\n\n' % node.rawsource)
    depart_target = passvisit

    def visit_title_reference(self, node):
        self.increment_index()
        self.body.append('`')
    def depart_title_reference(self, node):
        self.body.append('`')

    def visit_footnote(self, node):
        if 'auto' in node:
            if node.attributes['auto']:
                self.body.append(u'.. [#] ')
                self.context.indent = self.context.indent + u'   '
                self.context.parentrawsource = node.rawsource
                self.rawsourceindex = 0
                return
        #self.default_visit(node) #TODO
        self.in_footnote = 1
        self.body.append(".. [")
    def depart_footnote(self, node):
        self.body.append("\n")

    def visit_label(self, node):
        self.debugprint(node)
    def depart_label(self, node):
        if self.in_footnote:
            self.body.append("] ")

    # Images
    def visit_image(self, node):
        self.increment_index()
        self.in_image = 1
        if self.in_figure:
            self.body.append(node['uri'] +'\n')
        else:
            self.add_directive('image', node['uri'])
    def depart_image(self, node):
        self.in_image = 0

    def visit_figure(self, node):
        self.increment_index()
        self.index = 0
        self.in_figure = True
        self.body.append("\n.. figure:: ")
    def depart_figure(self, node):
        self.body.append("\n\n")
        self.in_figure = None
        del self.index

    # Misc. block level
    def visit_generated(self, node): pass
    def depart_generated(self, node): pass

    def visit_system_message(self, node): pass
    def depart_system_message(self, node): pass

    def visit_comment(self, node):
        self.assure_newblock()
        self.increment_index()
        self.add_indented('.. ')
        self.context.indent += u'   '
    def depart_comment(self, node):
        self.assure_newline()
        del self.context.indent

    def visit_topic(self, node):
        self.debugprint(node)
        if 'classes' in node:
            if 'contents' in node.attributes['classes']:
                raise nodes.SkipChildren
    def depart_topic(self, node):
        pass

    def visit_block_quote(self, node):
        if 'classes' in node:
            if 'epigraph' in node.attributes['classes']:
                self.visit_directive(node, name='epigraph')
                return
        self.assure_newblock()            
        self.increment_index()
        self.context.index = 0
        self.in_block_quote += 1
        self.context.indent += '   '
    def depart_block_quote(self, node):
        if 'classes' in node:
            if 'epigraph' in node.attributes['classes']:
                self.depart_directive(node, name='epigraph')
                return
        self.in_block_quote -= 1
        del self.context.index
        del self.context.indent

    def visit_literal_block(self, node):
        self.assure_newblock()
        self.increment_index()
        self.add_indented(':: ')
        self.context.indent += '   '
        self.assure_newblock()
        self.block_level = True
    def depart_literal_block(self, node):
        #self.assure_newblock()
        del self.context.indent
        self.block_level = False

#    def visit_attribution(self, node):
#        # @fixme: indent
#        self.body.append('---')
#    def depart_attribution(self, node):
#        self.body.append('\n')

    # XXX: what can lineblock contain
    def visit_line_block(self, node):
        self.increment_index()
        self.in_line_block = 1
        self.context.index = 0
    def depart_line_block(self, node):
        del self.context.index
        self.in_line_block = None
        self.body.append('\n')

    def visit_line(self, node):
        self.increment_index()
        self.context.index = 0
        self.body.append(' | ')
    def depart_line(self, node):
        del self.context.index
        self.body.append('\n')

    def visit_transition(self, node):
        self.increment_index()
        #self.body.append("\n----\n\n")
        self.body.append(u'%s\n\n' %node.rawsource)
    depart_transition = passvisit

    visit_problematic = passvisit
    depart_problematic = passvisit

    # Lists
    def visit_enumerated_list(self, node):
        if self.block_level and self.context.index:
            self.assure_newblock()
        self.increment_index()
        self.context.index = 0
        self.context.enumtype = node.attributes['enumtype']
        self.in_enumerated_list += 1
    def depart_enumerated_list(self, node):
        self.in_enumerated_list -= 1
        del self.context.index
        del self.context.enumtype
        #self.assure_newblock()

    def visit_bullet_list(self, node):
        if self.block_level and self.context.index:
            self.assure_newblock()
        self.increment_index()
        self.context.index = 0
        self.in_bullet_list += 1
        self.context.bullet = node.attributes['bullet']
    def depart_bullet_list(self, node):
        del self.context.index
        del self.context.bullet
        self.in_bullet_list -= 1
        #self.assure_newblock()
        #self.add_newline()

    def visit_list_item(self, node):
        #self.debugprint(,node)
        self.increment_index()
        self.context.index = 0
        if self.in_bullet_list:
            bullet_instance = u'%s ' % self.context.bullet
            self.add_indented(bullet_instance)
            lil = len(bullet_instance)
        elif self.in_enumerated_list:
            enum_instance = u'%s. ' % \
                    self.enumeration_symbol[self.context.enumtype]\
                                                   (self.context.previous('index'))
            self.add_indented(enum_instance)
            lil = len(enum_instance)
        else:
            raise Exception, "Illegal container for list item"
        self.context.indent += u' ' * lil
        self.block_level = False
    def depart_list_item(self, node):
        self.assure_newline()
        del self.context.indent
        del self.context.index
        self.block_level = True

    # Definition lists
    def visit_definition_list(self, node): 
        if self.block_level and self.context.index:
            self.assure_newblock()
    def depart_definition_list(self, node): pass

    def visit_definition_list_item(self, node): pass
    def depart_definition_list_item(self, node): pass

    def visit_term(self, node):
        self.block_level = False
    def depart_term(self, node): 
        self.add_newline()
        self.block_level = True

    def visit_definition(self, node):
        self.context.indent += '  '
        self.block_level = False
    def depart_definition(self, node):
        self.add_newline()
        del self.context.indent
        self.block_level = True


    # Field lists
    def visit_field_list(self, node):
        if self.block_level:
            self.assure_newblock()
        self.increment_index()
        self.in_field_list += 1
    def depart_field_list(self, node):
        self.in_field_list -= 1
        self.assure_newline()

    def visit_field(self, node):
        self.context.index = 0
    def depart_field(self, node):
        del self.context.index

    def visit_field_name(self, node):
        self.add_indented(":")
        self.block_level = False
    def depart_field_name(self, node):
        #self.add_indented(": ")
        self.body.append(": ")
        self.block_level = True

    def visit_field_body(self, node):
        if 'start_after_newline' in node:
            self.add_newline()
        self.context.indent += u'  '
    def depart_field_body(self, node):
        self.assure_newline()
        del self.context.indent

    # Docinfo field list
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
        self.add_indented('')

    # Tables
    def visit_entry(self, node):
        self.debugprint(node)
    depart_entry = passvisit

    def visit_row(self, node):
        self.debugprint(node)
    depart_row = passvisit

    def visit_thead(self, node):
        self.debugprint(node)
    depart_thead = passvisit

    def visit_tbody(self, node):
        self.debugprint(node)
    depart_tbody = passvisit

    def visit_tgroup(self, node):
        self.debugprint(node)
    depart_tgroup = passvisit

    def visit_table(self, node):
        self.debugprint(node)
    depart_table = passvisit

    def visit_colspec(self, node):
        self.debugprint(node)
    depart_colspec = passvisit

    def visit_caption(self, node):
        self.assure_newline()
    def depart_caption(self, node):
        self.assure_newline()

    # Decoration
    def visit_decoration(self, node):
        self.debugprint(node)
    def depart_decoration(self, node):
        pass

    def visit_right_margin(self, node):
        self.visit_directive(node, name='right_margin')
    def depart_right_margin(self, node):
        self.depart_directive(node, name='right_margin')

    def visit_left_margin(self, node):
        self.visit_directive(node, name='left_margin')
    def depart_left_margin(self, node):
        self.depart_directive(node, name='left_margin')

    docinfo_fields = ('author','authors','organization','contact','address',
                'status', 'date', 'version', 'revision', 'copyright',)

    admonition_fields = ('attention', 'caution', 'danger', 'warning', 'error',
            'hint', 'important', 'note', 'tip', 'admonition')

    def visit_citation(self, node):
        self.debugprint(node)
    depart_citation = passvisit        

    def visit_legend(self, node):
        self.debugprint(node)
    depart_legend = passvisit        

    directives = ('raw','epigraph','header','footer','sidebar','rubric','compound',
            )

    # Catch all
    def unknown_visit(self, node):
        cn = classname(node)
        if cn in self.docinfo_fields:
            self.increment_index()
            self.add_indented(':%s: ' % (cn.title())) # XXX
            return
        elif cn in self.admonition_fields:
            self.increment_index()
            return
        elif cn in self.directives:
            self.visit_directive(node)
            return
        #print "not visiting", node.__class__.__name__
        #return
        raise NotImplementedError(
            '%s visiting unknown node type: %s'
            % (self.__class__, node.__class__.__name__))

    def unknown_departure(self, node):
        cn = classname(node)
        if cn in self.docinfo_fields:
            return
        elif cn in self.admonition_fields:
            return
        elif cn in self.directives:
            self.depart_directive(node)
            return
        #print "still open", node.__class__.__name__
        #return
        raise NotImplementedError(
            '%s departing unknown node type: %s'
            % (self.__class__, node.__class__.__name__))

    # Generic handlers        
    def visit_directive(self, node, name=None):
        if not name:
            name = classname(node)
        self.increment_index()
        self.context.index = 0
        self.add_directive(name)
        self.context.indent += '   '
        # TODO: options
        # TODO: arguments/classes
    def depart_directive(self, node, name=None):
        del self.context.indent
        del self.context.index

    def debugprint(self, node):
        self.body.append("[XXX:%s %s]" % (node.tagname, self.context))

trailing_ws = re.compile('\S*(\s+)$')

def get_trailing_ws(string):
    m = trailing_ws.match(string)
    if m:
        return m.group(1)
    return ''

is_all_ws = re.compile('^\s+$').match

class ContextStack(object):
    """A stack of states. Setting an attribute overwrites the last
    value, but deleting the value reactivates the old one.
    Default values can be set on construction.
    
    This is used for important states during output of rst,
    e.g. indent level, last bullet type.
    """
    
    def __init__(self, defaults=None):
        '''Initialise _defaults and _stack, but avoid calling __setattr__'''
        if defaults is None:
            object.__setattr__(self, '_defaults', {})
        else:
            object.__setattr__(self, '_defaults', dict(defaults))
        object.__setattr__(self, '_stack', {})

    def __getattr__(self, name):
        '''Return last value of name in stack, or default.'''
        if name in self._stack:
            return self._stack[name][-1]
        if name in self._defaults:
            return self._defaults[name]
        raise AttributeError

    def __setattr__(self, name, value):
        '''Pushes a new value for name onto the stack.'''
        if name in self._stack:
            self._stack[name].append(value)
        else:
            self._stack[name] = [value]

    def __delattr__(self, name):
        '''Remove a value of name from the stack.'''
        if name not in self._stack:
            raise AttributeError
        del self._stack[name][-1]
        if not self._stack[name]:
            del self._stack[name]
   
    def depth(self, name):
        l = len(self._stack[name])
        if l:
            return l-1

    def previous(self, name):
        return self._stack[name][-2]

    def __repr__(self):
        return repr(self._stack)


def classname(obj):
    return obj.__class__.__name__



## Main/test

import docutils.core

def test(doc):
    print (' ' + doc).rjust(79, '=')
    rst = open(doc).read().decode('utf-8')
    original_tree = docutils.core.publish_parts(
            source=rst, 
            writer_name='pseudoxml')['whole']#writer_name='dotmpe-rst')
    result = docutils.core.publish_parts(
            source=rst, 
            writer=Writer())['whole']#writer_name='dotmpe-rst')
    generated_tree = docutils.core.publish_parts(
            source=result,
            writer_name='pseudoxml')['whole']
    print (' Original').rjust(79, '-')
    print rst.strip()
    print
    print (' Generated').rjust(79, '-')
    print result.strip()

    print (' Result').rjust(79, '-')
    print (rst == result) and "Lossless" or "Lossy"
    print (generated_tree == original_tree) and "PXML OK" or "PXML Mismatch"
    print


if __name__ == '__main__':
    import os, sys, glob

    if sys.argv[1:]:
        for doc in sys.argv[1:]:
            assert os.path.exists(doc) and doc.endswith('.rst'), doc
            test(doc)
    else:

        p = os.path.realpath(__file__)
        for i in range(0, 5):
            p = os.path.dirname(p)
        PROJ_ROOT = p
            
        TEST_DOC = filter(os.path.getsize,
                glob.glob(os.path.join(PROJ_ROOT, 'var', '*.rst')))
        TEST_DOC.sort()

        for doc in TEST_DOC:
            test(doc)

