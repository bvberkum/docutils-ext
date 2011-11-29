"""Parse and serialize docutils documents from and to reStructuredText.

XXX: This is a heavy work in progress. RstTranslator has some issues with
     inline nodes and does not do tables.

"""
import math
import re
import roman

from docutils import nodes, writers



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

        self.output = visitor.astext()


class RstTranslatorCommon(nodes.NodeVisitor):
    def _attr(self, node, name):
        if name in node and node[name]:
            return node[name]


class RstPreTranslator(RstTranslatorCommon):

    """
    """

    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        #self.settings = settings = document.settings
        self.id_references = {}
        self.uri_references = {}
        self.anonymous_references = {}

    def visit_reference(self, node):
        anonymous = self._attr(node, 'anonymous')
        classes = self._attr(node, 'classes')
        ref_uri = self._attr(node, 'refuri')
        ref_id = self._attr(node, 'refid')
        if ref_id:
            self.id_references[ref_id] = node
        print node['names'], locals()

    def unknown_visit(self, node): pass
    def unknown_departure(self, node): pass


INDENT = u'  '
section_adornments = ['=', '-', '~', '^', '+', "\"", "'", "_"]

class RstTranslator(RstTranslatorCommon):

    """
    Visit docutils tree and serialize to rSt.
    """

    context = None
    "Context to stack variables during node traversal. "

    debug = False
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
    "Map to symbol generators. "

    capture_text = None
    "Concatenate Text nodes onto `key` on context. "

    allow_body_adjacent = [
            'title',
            'comment',
            'footnote',
            'substitution_definition',
        ] # + directives
    "XXX: this may replace force_block_level?"

    body = []
    "The list of document strings, to be concatenated to final file. "

    #docinfo = {}
    #targets = {}

    anonymous_role_count = 0 

    def __init__(self, document, pretranslator):
        nodes.NodeVisitor.__init__(self, document)
        for attr in 'id_references', 'uri_references', 'anonymous_references':
            setattr(self, attr, getattr(pretranslator, attr))
        self.settings = settings = document.settings
        self.force_block_level = False
        """Prevent blank line insert, allows override by previous sibling. """
        self.preserve_ws = False
        self.capture_text = None
        self.skip_content = None
        self.section_adornments = section_adornments        
        self.roles = []
        #self.docinfo = {}
        self.body = []
        #self.targets = {}
        self.context = ContextStack(defaults={
                'tree': [],
                'bullet': u'',
                'indent': u'',
                'section_adornment': self.section_adornments[0],
                'enumtype': u'',
                'title': None,
                'subtitle': None,
                'index': None,
                'block': None,
                'offset': None,
            })

    def sub_tree(self, node):
        self.context.append('tree', node)

    @property
    def block_level(self):
        if self.force_block_level:
            return True
        if self.context.index:
            return False
        return self.context.tree[-2].tagname in (
                'document', 
                'section', 
                'footnote',
                'list_item',
                'definition', 
                'field_body')

    def pop_tree(self):
        if self.context.tree[-1].tagname in ('title', 'label'):
            self.force_block_level = True
        elif self.force_block_level:
            self.force_block_level = False
        del self.context.tree

    @property
    def current_path(self):
        return "/".join([n.tagname for n in self.context.tree])

    @property
    def current_node(self):
        return self.context.tree[-1]

    def in_tag(self, other_name=None, sup=0):
        node = self.current_node
        tagname = node.tagname
        while sup and node.parent:
            if sup == '*':
                if other_name and (tagname == other_name):
                    return True
            node = node.parent
            tagname = node.tagname
            if sup != '*':
                sup -= 1

        if other_name:
            return tagname == other_name
        else:
            return tagname

    @property
    def root(self):
        return not self.current_node.parent

    @property
    def previous_sibling(self):
        assert self.context.index > 0
        #prev_idx = self.context.previous('index')
        node = self.current_node
        if self.root:
            return
        pi = node.parent.index(node)
        return node.parent.children[pi-1]

    def astext(self):
        return "".join(self.body)

        # TODO: handle all that support the class option, and others
        #classes = node.attributes['classes']
        #if classes:
        #    self._write_directive('class',*classes)

    def _write_indented(self, *lines):
        """
        Write one or more lines. The indent on the context is used to prefix the
        text. 

        The 'indented' variable indicates the lenght the current line is padded.
        """
        _lines = list(lines)
        indent = self.context.indent
        while _lines:
            text = _lines.pop(0)

            if self.preserve_ws:
                self.body.append(indent + text)
                self._write_newline()
                continue

            # write line from indent and text
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
                self._assure_emptyline()
            else:
                self.indented += cindent

    def _write_directive(self, name, *args, **kwds):
        if not self.block_level:
            self._assure_newblock()
        self._write_indented(
                u".. %s:: %s" % (name, ' '.join(args)))
        if kwds:
            self._write_options(kwds)
            
    def _write_options(self, opts):
        self.context.indent += INDENT
        for name in opts:
            self._assure_emptyline()
            value = opts[name]
            self._write_indented(":%s:" % name)
            self.context.indent += INDENT
            if isinstance(value, list):
                self._write_indented(' '+" ".join(value))
            del self.context.indent
        del self.context.indent

    def add_role(self, name, inherit, opts):
        if not name:
            self.anonymous_role_count += 1
            name = 'inline_role%i'% self.anonymous_role_count
        #if self.block_level:
        #    self._write_role(name, inherit, opts)
        #else:
        self.roles.append((name, inherit, opts))
        return name
   
    def _write_role(self, name, inherit, opts):
        assert name
        arg = name
        if inherit:
            arg += "(%s)" % inherit
        if not opts['class']:
            del opts['class']
        self._write_directive('role', arg, **opts)
        return name

    def debugprint_indent(self):                        
        if self.debug or self.debug_indent:
            if self.indented:
                self.body.append("(%i/%i)" % (self.indented,
                    len(self.context.indent)))
            else:
                self.body.append("(%i)" % 
                    len(self.context.indent))

    def _write_newline(self):
        self.body.append('\n') # XXX: unix
        self.indented = 0

    @property
    def current_whitespace(self):
        "The bodies' trailing whitespace. "
        if not self.body:
            return
        idx = len(self.body)-1
        ws = ''
        while idx > -1:
            str_part = self.body[idx]
            if str_part:
                ws = get_trailing_ws(str_part) + ws
            if str_part and not is_all_ws(str_part):
                break
            idx -= 1
        ws2 = list(ws); ws2.reverse()
        return ''.join(ws)

    def _assure_emptyline(self, cnt=1):
        if not self.body:
            return
        ws = self.current_whitespace
        newlines = re.sub(r'[^\n]', '', ws) # XXX: unix
        while len(newlines) < cnt:
            self._write_newline()
            cnt -= 1

    def _assure_newblock(self):
        if not self.body:
            return
        if self.context.index > 0 and self.previous_sibling:
            if self.in_tag(self.previous_sibling.tagname):
                if self.in_tag() in self.allow_body_adjacent:
                    self._assure_emptyline()
                    return
        if self.context.index == 0:
            return
        ws = self.current_whitespace
        newlines = len(re.sub(r'[^\n]', '', ws)) # XXX: unix
        if newlines < 1:
            self._write_newline()
        if newlines < 2:
            self._write_newline()

    def increment_index(self):
        idx = self.context.index + 1
        del self.context.index
        self.context.index = idx

    def _pass_visit(self, node):
        "No-op to prevent catch-all handlers. "

    # NodeVisitor hooks

    def visit_document(self, node):
        self.sub_tree(node)
        self.context.index = 0

    def depart_document(self, node):
        # finalize
        for name, inherit, opts in self.roles:
            self._write_role(name, inherit, opts)

        self.pop_tree()
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
        if not self.skip_content:
            self._write_indented(*lines)
    def depart_Text(self, node):
        pass

    def visit_title(self, node):
        self.sub_tree(node)
        self.increment_index()
        previous_tree = self.context.previous('tree')
        if previous_tree and previous_tree[-1].tagname == 'topic':
            if not self.block_level:
                self._assure_newblock()
            self.visit_field_name(node)
        else:
            self.capture_text = 'title'
    def depart_title(self, node):
        self.pop_tree()
        prev_tree = self.context.previous('tree')
        if prev_tree and prev_tree[-1].tagname == 'topic':
            self.depart_field_name(node)
            self.context.indent += INDENT
        else:
            self.capture_text = None
            text = self.context.title
            del self.context.title
            self._assure_emptyline()
            self._write_indented( self.context.section_adornment * len(text))
        self._assure_emptyline()

    def visit_subtitle(self, node):
        self.sub_tree(node)
        self.capture_text = 'subtitle'
    def depart_subtitle(self, node):
        self.pop_tree()
        self.capture_text = None
        text = self.context.subtitle
        self._assure_emptyline()
        seca = self.context.section_adornment
        subindex = self.section_adornments.index(seca) + 2
        assert len(self.section_adornments) >= subindex, subindex
        self._write_indented(self.section_adornments[subindex] * len(text))
        self._assure_emptyline()
        del self.context.subtitle

    def visit_section(self, node):
        self.sub_tree(node)
        if not self.block_level:
            self._assure_newblock()
        self.increment_index()
        self.context.index = 0
        newlevel = self.context.depth('index')
        self.context.section_adornment = self.section_adornments[newlevel]
    def depart_section(self, node):
        self.pop_tree()
        self._assure_emptyline()
        del self.context.index
        del self.context.section_adornment

    def visit_paragraph(self, node):
        self.sub_tree(node)
        if not self.block_level:
            self._assure_newblock()
        self.increment_index()
        self.context.index = 0            

    def depart_paragraph(self, node):
        self._assure_newblock()
        del self.context.index
        self.pop_tree()

    # Inline
    def visit_inline(self, node):
        self.sub_tree(node)
        self.increment_index()
        # 'Parse' class-list
        classes = list(node['classes'])
        name = None
        inherit = []
        if classes:
            for klass in classes:
                if klass in ('emphasis', 'strong', 'literal'): # Du internal
                    classes.remove(klass)
                    inherit.append(klass)
            # First next classname is role-name; best we can do
            if classes:
                name = classes.pop(0)
        print 'role', name, inherit, classes
        role = self.add_role(name, " ".join(inherit), {'class': classes})
        self._write_indented(':%s:`' % role)
    def depart_inline(self, node):
        self.pop_tree()
        self._write_indented('`')

    def _visit_simple_inline(self, klass, decoration, node):
        if self._attr(node, 'classes'):
            if klass:
                node['classes'].append(klass)
            self.visit_inline(node)
        else:
            self.sub_tree(node)
            self.increment_index()
            self._write_indented(decoration)

    def _depart_simple_inline(self, klass, decoration, node):
        if self._attr(node, 'classes'):
            self.depart_inline(node)
        else:
            self.pop_tree()
            self.body.append(decoration)

    def visit_emphasis(self, node):
        self._visit_simple_inline('emphasis', '*', node)
    def depart_emphasis(self, node):
        self._depart_simple_inline('emphasis', '*', node)

    def visit_strong(self, node):
        self._visit_simple_inline('strong', '**', node)
    def depart_strong(self, node):
        self._depart_simple_inline('strong', '**', node)

    def visit_literal(self, node):
        self._visit_simple_inline('literal', '``', node)
    def depart_literal(self, node):
        self._depart_simple_inline('literal', '``', node)

    visit_subscript = _pass_visit
    depart_subscript = _pass_visit

    visit_superscript = _pass_visit
    depart_superscript = _pass_visit

    def visit_attribution(self, node):
        self.sub_tree(node)
        self.increment_index()
        self._assure_newblock()
        self._write_indented('-- ')
    def depart_attribution(self, node):
        self.pop_tree()
        self._assure_newblock()

    visit_description = _pass_visit
    depart_description = _pass_visit

    visit_doctest_block = _pass_visit
    depart_doctest_block = _pass_visit

    # Option lists
    def visit_option_list(self, node):
        self.sub_tree(node)
        if not self.block_level:
            self._assure_newblock()
        self.increment_index()
        self.context.index = 0
        #self.context.indent += 5 * INDENT
    def depart_option_list(self, node):
        self.pop_tree()
        del self.context.index
        #del self.context.indent
        self._assure_emptyline()

    visit_option_list_item = _pass_visit
    depart_option_list_item = _pass_visit

    visit_option_group = _pass_visit
    depart_option_group = _pass_visit

    visit_option_string = _pass_visit
    depart_option_string = _pass_visit

    visit_option = _pass_visit
    depart_option = _pass_visit

    visit_option_argument = _pass_visit
    depart_option_argument = _pass_visit

    # References
    def visit_reference(self, node):
        self.sub_tree(node)
        self.increment_index()
        if not self.root and self.in_tag('figure', '*'):
            pass
        else:
            if 'refuri' in node:
                if node.astext() == node['refuri']:
                    pass
                else:
                    self._write_indented('`')
            elif 'refid' in node:
                self._write_indented('`')
                #self.debugprint(node)

    def depart_reference(self, node):
        if self.in_tag('figure', '*'):
            self._write_indented(":target: %s\n\n" %node['refuri'])
            self.indented = 0
        else:
            if 'refuri' in node:
                if node.astext() == node['refuri']:
                    pass
                elif 'anonymous' in node:
                    self.body.append('`__')
                else:
                    self.body.append('`_')
            elif 'refid' in node:
                self.body.append('`_')
        self.pop_tree()

    def visit_footnote_reference(self, node):
        self.sub_tree(node)
        self.increment_index()
        self._write_indented('[')
    def depart_footnote_reference(self, node):
        self.pop_tree()
        self.body.append(']_ ')

    def visit_substitution_definition(self, node):
        self.sub_tree(node)
        self.increment_index()
        #print 'substitution_definition', node
        #TODO: unicode
        self.body.append('.. |%s| replace:: ' % node['names'][0])
    def depart_substitution_definition(self, node):
        self.pop_tree()
        self._write_newline()

    def visit_citation_reference(self, node):
        self.sub_tree(node)
        self.increment_index()
        self.body.append('[')
    def depart_citation_reference(self, node):
        self.pop_tree()
        self.body.append(']_ ')

    def visit_target(self, node):
        self.sub_tree(node)
        ref_uri = self._attr(node, 'refuri')
        ref_id = self._attr(node, 'refid')
        if ref_uri or ref_id:
            if not self.block_level:
                self._assure_newblock()
        self.increment_index()
        if 'anonymous' in node and node['anonymous'] == '1':
            self._write_indented('.. __:')
        elif 'refid' in node or 'refuri' in node:
            self._write_indented('.. _')
        if ref_uri:
            # XXX: what about multiple names?
            if 'names' in node and node['names']:
                self._write_indented("%s: %s" % (node['names'][0],
                    ref_uri))
            else:
                self._write_indented("`")
        elif ref_id:
            if 'names' in node and node['names']:
                self._write_indented("%s: `%s`_" % (node['names'][0],
                    ref_id))
            else:
                self._write_indented("`")
        else:
            self._write_indented('')
    def depart_target(self, node):
        self.pop_tree()
        if 'refuri' not in node or not node['refuri']:
            pass
        if 'refid' not in node or not node['refid']:
            self._write_indented('')

    def visit_title_reference(self, node):
        self.sub_tree(node)
        self.increment_index()
        self._write_indented('`')
    def depart_title_reference(self, node):
        self._write_indented('`')
        self.pop_tree()

    def visit_footnote(self, node):
        self.sub_tree(node)
        if not self.block_level:
            self._assure_newblock()
        self.increment_index()
        self.context.index = 0
        if 'auto' in node:
            if node.attributes['auto']:
                self._write_indented(u'.. [#] ')
                #self.context.parentrawsource = node.rawsource
                self.context.indent += INDENT
                self.rawsourceindex = 0
                self.skip_label = True
                return
        #self.default_visit(node) #TODO
        self._write_indented(".. [")
        self.context.indent += INDENT
    def depart_footnote(self, node):
        del self.context.index
        self.pop_tree()
        del self.context.indent
        #if 'auto' in node:
        #    if node.attributes['auto']:
        #        del self.context.indent
        #else:

    def visit_label(self, node):
        self.sub_tree(node)
        if self.in_tag('footnote', 1):
            if self.body[-1][-3:] == '#] ':
                self.skip_content = True
        #self.debugprint(node)
    def depart_label(self, node):
        self.pop_tree()
        if self.in_tag('footnote'):
            if self.skip_content:
                #self.debugprint(node)
                self.skip_content = False
            else:
                self.body.append("] ")
        elif self.in_tag('citation'):
            self.body.append('] ')

    # Images
    def visit_image(self, node):
        self.sub_tree(node)
        self.increment_index()
        if self.in_tag('figure', '*'):
            self.body.append(node['uri'])
            self._write_newline()
        else:
            self._assure_newblock()
            self._write_directive('image', node['uri'])
    def depart_image(self, node):
        self.pop_tree()

    def visit_figure(self, node):
        self.sub_tree(node)
        self.increment_index()
        self.index = 0
        self._assure_newblock()
        self.body.append(".. figure:: ")
        self.context.indent += INDENT
    def depart_figure(self, node):
        self.pop_tree()
        del self.index

    # Misc. block level
    def visit_generated(self, node): pass
    def depart_generated(self, node): pass

    def visit_system_message(self, node): pass
    def depart_system_message(self, node): pass

    def visit_comment(self, node):
        self.sub_tree(node)
        if not self.block_level:
            self._assure_newblock()
        self.increment_index()
        self._write_indented('.. ')
        self.context.indent += INDENT
    def depart_comment(self, node):
        self.pop_tree()
        self._assure_emptyline()
        del self.context.indent

    def visit_topic(self, node):
        self.sub_tree(node)
        #self.debugprint(node)
        if 'classes' in node:
            if 'contents' in node.attributes['classes']:
                raise nodes.SkipChildren
            for node_name in 'abstract', 'dedication':
                if node_name in node.attributes['classes']:
                    return
        self.visit_directive(node, name='topic')
    def depart_topic(self, node):
        if 'classes' in node:
            for node_name in 'abstract', 'dedication':
                if node_name in node.attributes['classes']:
                    del self.context.indent
        self.pop_tree()

    def visit_block_quote(self, node):
        #self.debugprint(node)
        if 'classes' in node:
            if 'epigraph' in node.attributes['classes']:
                self.visit_directive(node, name='epigraph')
                return
        self.sub_tree(node)
        self._assure_newblock()            
        self.increment_index()
        self.context.index = 0
        self.context.indent += '  '
    def depart_block_quote(self, node):
        if 'classes' in node:
            if 'epigraph' in node.attributes['classes']:
                self.depart_directive(node, name='epigraph')
                #print self.current_path, self.indented, len(self.context.indent)
                return
        self.pop_tree()
        del self.context.index
        del self.context.indent

    def visit_literal_block(self, node):
        self._assure_newblock()
        self.increment_index()
# FIXME: cannot distinguish between literal block and parsed literal block?
        if 'xml:space' in node and node['xml:space'] == 'preserve':
            self._write_directive('parsed-literal')
        else:
            self._write_indented(':: ')
        self.context.indent += '   '
        self._assure_newblock()
        self.preserve_ws = True
    def depart_literal_block(self, node):
        self._assure_newblock()
        del self.context.indent
        self.preserve_ws = False

#    def visit_attribution(self, node):
#        # @fixme: indent
#        self.body.append('---')
#    def depart_attribution(self, node):

    # XXX: what can lineblock contain
    def visit_line_block(self, node):
        self.sub_tree(node)
        if not self.block_level:
            self._assure_newblock()
        self.increment_index()
        #self._assure_emptyline(2)
        self.context.index = 0
    def depart_line_block(self, node):
        del self.context.index
        self.pop_tree()
        self._assure_newblock()
        self._assure_emptyline()

    def visit_line(self, node):
        self.sub_tree(node)
        self.increment_index()
        self._write_indented('| ')
        self.context.indent += INDENT
        self.context.index = 0
    def depart_line(self, node):
        del self.context.indent
        del self.context.index
        self.pop_tree()
        self._assure_emptyline()

    def visit_transition(self, node):
        while self.context.tree[-1].tagname not in ('section', 'document'):
            self.pop_tree()
        if not self.block_level:
            self._assure_newblock()
        self.increment_index()
        self.body.append(u'%s\n\n' %node.rawsource)
        self.indented = 0
    depart_transition = _pass_visit

    visit_problematic = _pass_visit
    depart_problematic = _pass_visit

    # Lists
    def visit_enumerated_list(self, node):
        self.sub_tree(node)
        if not self.block_level or self.context.index:
            self._assure_newblock()
        self.increment_index()
        self.context.index = 0
        if 'start' in node:
            self.context.offset = node.attributes['start']
        self.context.enumtype = node.attributes['enumtype']
    def depart_enumerated_list(self, node):
        self.pop_tree()
        if 'start' in node:
            self.context.offset
        del self.context.index
        del self.context.enumtype
        #self._assure_newblock()

    def visit_bullet_list(self, node):
        self.sub_tree(node)
        if not self.block_level:
            self._assure_newblock()
        self.increment_index()
        self.context.index = 0
        self.context.bullet = node.attributes['bullet']
    def depart_bullet_list(self, node):
        del self.context.index
        del self.context.bullet
        self.pop_tree()

    def visit_list_item(self, node):
        #self.debugprint(,node)
        self.sub_tree(node)
        self.increment_index()
        self.context.index = 0
        if self.in_tag('bullet_list', 1):
            bullet_instance = u'%s ' % self.context.bullet
            self._write_indented(bullet_instance)
            lil = len(bullet_instance)
        elif self.in_tag('enumerated_list', 1):
            enum_instance = u'%s. ' % \
                    self.enumeration_symbol[self.context.enumtype]\
                                                   (self.context.previous('index'))
            self._write_indented(enum_instance)
            lil = len(enum_instance)
        else:
            raise Exception, "Illegal container for %s %s, %s" % (self.in_tag(),
                    self.current_path, self.in_tag(None, 1))
        self.context.indent += u' ' * lil
    def depart_list_item(self, node):
        self._assure_emptyline()
        del self.context.indent
        self.pop_tree()
        del self.context.index

    # Definition lists
    def visit_definition_list(self, node): 
        self.sub_tree(node)
        if not self.block_level:
            self._assure_newblock()
        self.increment_index()
        #self.expect('definition_list_item')
        self.context.index = 0
    def depart_definition_list(self, node): 
        self.pop_tree()
        del self.context.index

    def visit_definition_list_item(self, node):
        self.sub_tree(node)
        #self.expect('term', 'classifier', 'definition')
        self.increment_index()
    def depart_definition_list_item(self, node):
        self.pop_tree()
        self._assure_emptyline()

    def visit_term(self, node):
        self.sub_tree(node)
        self.increment_index()
    def depart_term(self, node): 
        self._assure_emptyline()
        self.pop_tree()

    visit_classifier = _pass_visit
    depart_classifier = _pass_visit

    def visit_definition(self, node):
        self.sub_tree(node)
        self.increment_index()
        self.context.index = 0
        self.context.indent += INDENT
    def depart_definition(self, node):
        self._write_newline()
        self.pop_tree()
        del self.context.index
        del self.context.indent


    # Field lists
    def visit_field_list(self, node):
        self.sub_tree(node)
        if not self.block_level:
            self._assure_newblock()
        self.increment_index()
        self.context.index = 0
    def depart_field_list(self, node):
        self.pop_tree()
        del self.context.index
        self._assure_emptyline()

    def visit_field(self, node):
        self.sub_tree(node)
        self.increment_index()
    def depart_field(self, node):
        self.pop_tree()

    def visit_field_name(self, node):
        self.sub_tree(node)
        self._write_indented(":")
    def depart_field_name(self, node):
        self.pop_tree()
        #self._write_indented(": ")
        self.body.append(": ")

    def visit_field_body(self, node):
        self.sub_tree(node)
        #XXX: fmt opts: if 'start_after_newline' in node:
        #    self._write_newline()
        self.context.index = 0
        self.context.indent += INDENT
    def depart_field_body(self, node):
        self.pop_tree()
        self._assure_emptyline()
        del self.context.index
        del self.context.indent

    # Docinfo field list
    def visit_docinfo(self, node):
        self.sub_tree(node)

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
        self.pop_tree()
        self._write_indented('')

    # Tables
    def visit_entry(self, node):
        self.debugprint(node)
    depart_entry = _pass_visit

    def visit_row(self, node):
        self.debugprint(node)
    depart_row = _pass_visit

    def visit_thead(self, node):
        self.debugprint(node)
    depart_thead = _pass_visit

    def visit_tbody(self, node):
        self.debugprint(node)
    depart_tbody = _pass_visit

    def visit_tgroup(self, node):
        self.debugprint(node)
    depart_tgroup = _pass_visit

    def visit_table(self, node):
        self.debugprint(node)
    depart_table = _pass_visit

    def visit_colspec(self, node):
        self.debugprint(node)
    depart_colspec = _pass_visit

    def visit_caption(self, node):
        self.sub_tree(node)
        # first paragraph in figure
        self._assure_newblock()
        self.increment_index()
    def depart_caption(self, node):
        self.pop_tree()

    def visit_legend(self, node):
        # other paragraphs in figure
        self.sub_tree(node)
        self._assure_newblock()
        self.increment_index()
    def depart_legend(self, node):
        self.pop_tree()

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
        self.sub_tree(node)
        self._write_indented('.. [')
        self.context.indent += INDENT
    def depart_citation(self, node):
        del self.context.indent
        self.pop_tree()

    directives = ('raw','epigraph','header','footer','sidebar','rubric','compound',
            )

    # Catch all
    def unknown_visit(self, node):
        cn = classname(node)
        self.sub_tree(node)
        if cn in self.docinfo_fields:
            self.increment_index()
            self._write_indented(':%s: ' % (cn.title())) # XXX
            self.context.index = 0
            self.context.indent += '  '
            return
        elif cn in self.admonition_fields:
            self.increment_index()
            return
        elif cn in self.directives:
            self.visit_directive(node)
            return
        raise NotImplementedError(
            '%s visiting unknown node type: %s'
            % (self.__class__, node.__class__.__name__))

    def unknown_departure(self, node):
        cn = classname(node)
        self.pop_tree()
        if cn in self.docinfo_fields:
            del self.context.index
            del self.context.indent
            self._assure_emptyline()
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
        if not self.block_level:
            self._assure_newblock()
        self.sub_tree(node)
        if not name:
            name = classname(node)
        self.increment_index()
        self.context.index = 0
        self._write_directive(name)
        self.context.indent += '   '
        # TODO: options
        # TODO: arguments/classes
    def depart_directive(self, node, name=None):
        self.pop_tree()
        del self.context.indent
        del self.context.index

    def debugprint(self, node):
        self.body.append("[XXX:%s %r %r %r %s]" % (node.tagname, self.context.index,
            self.indented, self.context.indent, node['classes']))

trailing_ws = re.compile('^.*(?<!\s)(\s+)$')

def get_trailing_ws(string):
    assert isinstance(string, str) or isinstance(string, unicode), string
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

    def append(self, name, value):
        l = list(getattr(self, name))
        l.append(value)
        setattr(self, name, l)

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
        if len(self._stack[name]) > 1:
            return self._stack[name][-2]

    def __repr__(self):
        return repr(self._stack)


def classname(obj):
    return obj.__class__.__name__



## Main/test

def print_compare(doc, width=79):
    import docutils.core

    out = []
    out += [ (' ' + doc).rjust(width, '=')]
    rst = open(doc).read().decode('utf-8')
    assert isinstance(rst, unicode)

    original_tree = docutils.core.publish_parts(
            source=rst, 
            writer_name='pseudoxml')['whole']#writer_name='dotmpe-rst')
    assert isinstance(original_tree, unicode)
    result = docutils.core.publish_parts(
            source=rst, 
            writer=Writer())['whole']#writer_name='dotmpe-rst')
    assert isinstance(result, unicode)
    try:
        generated_tree = docutils.core.publish_parts(
                source=result,
                writer_name='pseudoxml')['whole']
    except Exception, e:
        generated_tree = u''
    assert isinstance(generated_tree, unicode)

    if width >= 79*2+1:

        original_out = original_tree.strip().split('\n')
        generated_out = generated_tree.strip().split('\n')
        out += [ (u'Original Tree ').ljust(79, '-') +u' '+ (u'Generated Tree ').ljust(79, '-') ] 
        while original_out or generated_out:
            p1 = u''
            p2 = u''
            if original_out:
                p1 = original_out.pop(0)
            if generated_out:
                p2 = generated_out.pop(0)
            out += [ p1.ljust(79) +u' '+ p2.ljust(79) ]
        out += [u''] 

        # print side-by-side view
        original_out = rst.strip().split('\n')
        generated_out = result.strip().split('\n')
        out += [ (u'Original ').ljust(79, '-') +u' '+ (u'rST rewriter ').ljust(79, '-') ] 
        while original_out or generated_out:
            p1 = u''
            p2 = u''
            if original_out:
                p1 = original_out.pop(0)
            if generated_out:
                p2 = generated_out.pop(0)
            # TODO: wrap lines
            #if len(p1) > 79 or len(p2) > 79:
            out += [ p1.ljust(79) +u' '+ p2.ljust(79) ]
        out += [u''] 

    else:

        out += [ ('Original ').ljust(width, '-') ]
        out += [ rst.strip(), u'']

        out += [ ('Generated ').ljust(width, '-') ] 
        out += [ result.strip(), u'' ]

    out += [ ('Result ').ljust(width, '-')]
    listwidth = int(width * 0.25)
    out += [ 'File:'.rjust(listwidth, ' ') +' '+ doc ]
    if generated_tree == original_tree:
        out += [ 'Doctree Comparison:'.rjust(listwidth, ' ') +" PXML match" ]
        out += [ 'Source Comparison:'.rjust(listwidth, ' ') +' '+ \
                ((rst == result) and "Lossless" or "Lossy")]
    else:
        out += [ 'Doctree Comparison:'.rjust(listwidth, ' ') +" Error: PXML mismatch" ]
    out += [u'']

    print u"\n".join(out)


if __name__ == '__main__':
    import os, sys, glob

    if sys.argv[1:]:
        for doc in sys.argv[1:]:
            assert os.path.exists(doc) and doc.endswith('.rst'), doc
            print_compare(doc, width=159)
    else:

        p = os.path.realpath(__file__)
        for i in range(0, 5):
            p = os.path.dirname(p)
        PROJ_ROOT = p
        
        TEST_DOC = [
#            'var/test-10.literal-block-1.rst',
#            'var/test-1.document-6.rst',
#            'var/test-1.document-7.rst',
#            'var/test-5.inline-1.rst',
            'var/test-5.inline-2.rst',
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
            print_compare(doc, width=159)

