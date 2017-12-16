# pylint: disable=no-member
"""Parse and serialize docutils documents from and to reStructuredText.

XXX: This is a heavy work in progress. RstTranslator has some issues with
     inline nodes and does not do tables.

     There are no extra options at all, and not really a reader/parser to go
     with it yet.
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


class AbstractTranslator(nodes.NodeVisitor):
    pass

class RstPreTranslator(AbstractTranslator):

    """
    Pre-pass document visitor. Accumulates indices.
    """

    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        #self.settings = settings = document.settings
        self.id_references = {}
        self.uri_references = {}
        self.anonymous_references = {}
        self.targets = {} # target id -> refid or refuri

    def visit_target(self, node):
        pass
        #for i in ids.split(' '):
        #    self.targets[i] =

    def visit_reference(self, node):
        # ????
        anonymous = node.get('anonymous')
        classes = node.get('classes')
        refuri = node.get('refuri')
        refid = node.get('refid')
        if refid:
            self.id_references[refid] = node

    def unknown_visit(self, node): pass
    def unknown_departure(self, node): pass


INDENT = u'  '
quote_chars = '!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'

class RstTranslator(AbstractTranslator):

    """
    Visit docutils tree and serialize to rSt.
    """

    debug = False
    debug_indent = False

    section_adornments = tuple('=-~^+"_`')

    enumeration_symbol = {
        'arabic': lambda i: str(i),
        'loweralpha': lambda i: chr(i+ord('a')-1),
        'upperalpha': lambda i: chr(i+ord('A')-1),
        'upperroman': lambda i: roman.toRoman(i).upper(),
        'lowerroman': lambda i: roman.toRoman(i).lower(),
    }
    "Map to symbol generators. "

    allow_body_adjacent = [
            'title',
            'comment',
            'footnote',
            'substitution_definition',
        ] # + directives
    "These may be 'touching' without blankline separation. XXX: this may replace force_block_level?"

    #docinfo = {}
    #targets = {}

    def __init__(self, document, pretranslator):
        nodes.NodeVisitor.__init__(self, document)
        # fetch indices from RstPreTranslator
        for attr in 'id_references', 'uri_references', 'anonymous_references':
            setattr(self, attr, getattr(pretranslator, attr))

        self.settings = settings = document.settings
        self.force_block_level = False
        """Prevent blank line insert, allows override by previous sibling. """
        self.context = None
        "Context to stack variables during node traversal. "
        self.indented = 0
        "The offset already indented by the current line (substract from context.indent). "
        self.section_adornments = [] # 0 is doctitle, then sectiontitles.
        "The sequence of section adornments. "
        self.subtitle_adornment = None
        self.capture_text = None
        "Concatenate Text nodes onto `key` on context. "
        self.body = []
        "The list of document strings, to be concatenated to final file. "
        self.anonymous_role_count = 0

        self.preserve_ws = False
        self.capture_text = False
        self.skip_content = False
        self.tab_content = ()
        self.inline = False
        self.roles = []
        #self.docinfo = {}
        self.body = []
        #self.targets = {}
        """Each stack level represents some node, but not all nodes need a
        stacklevel though we may end up with that.
        The stack is increased simply by setting a property, to replace a value
        use replace or increment functions.
        """
        self.context = ContextStack(defaults={
                # a list of all the elements up to the level, though not all
                'tree': [],
                'bullet': u'',
                'indent': u'',
                #'section_adornment': self.section_adornments[0],
                'enumtype': u'',
                'title': None,
                'subtitle': None,
                'index': None,
                'block': None,
                'offset': None,
                'parsed': False,
            })
        self.doclevel = 0

    def sub_tree(self, node):
        self.context.append('tree', node)

    def pop_tree(self):
        if self.context.tree[-1].tagname in ('title', 'label'):
            self.force_block_level = True
        elif self.force_block_level:
            self.force_block_level = False
        del self.context.tree

    @property
    def block_level(self):
        if self.force_block_level:
            return True
        if self.context.index:
            return False
        if len(self.context.tree) < 2:
            return False
        return self.context.tree[-2].tagname in (
                'document',
                'section',
                'footnote',
                'list_item',
                'definition',
                'field_body')

    @property
    def path(self):
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

    def get_new_section_adornment(self):
        adornments = list(self.__class__.section_adornments)
        adornment = adornments.pop(0)
        used = self.section_adornments + [ self.subtitle_adornment ]
        while adornment in used:
            assert adornments, "Ran out of adornments: %s" % used
            adornment = adornments.pop(0)
        return adornment

    def sub_section(self):
        adornment = self.get_new_section_adornment()
        self.section_adornments.append(adornment)
        assert self.doclevel == len(self.section_adornments), (self.doclevel,
                len(self.section_adornments), self.section_adornments)

    @property
    def adornment(self):
        return self.section_adornments[self.doclevel-1]

    def set_title_adornment(self):
        adornments = list(self.__class__.section_adornments)
        if self.doclevel > len(self.section_adornments):
            self.sub_section()

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

            if self.preserve_ws and not self.context.parsed:
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

    def _write_tabbed(self, *lines):#cols=0, fields=(), tabs=()):
        """I guess this is a first step to writing tables also?
        option lists need special tabbed blocks, not just indented blocks
        but block-aligned content besides content.
        """

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

    def last_string(self, length=1):
        assert length == 1
        x = -1
        bl = len(self.body)
        while bl+x > -1:
            y = -1
            while len(self.body[x])+y > -1:
                c = self.body[x][y]
                if not c.isspace():
                    return bl+x, len(self.body[x])+y, c
                y -= 1
            x -= 1
        return -1, -1, None

    def insert(self, x, y, s):
        "Insert string in body text node."
        text = self.body[x]
        text = text[:y] +s+ text[y:]
        self.body[x] = text

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

    def _pass_visit(self, node):
        "No-op to prevent catch-all handlers. "

    # NodeVisitor hooks

    def visit_document(self, node):
        self.sub_tree(node)
        self.context.index = 0
        self.doclevel += 1
        self.set_title_adornment()

    def depart_document(self, node):
        # finalize
        for name, inherit, opts in self.roles:
            self._write_role(name, inherit, opts)

        self.pop_tree()
        del self.context.index
        self.doclevel -= 1

    def visit_Text(self, node):
        """At the leafs of the three there are the textnodes, the actual stream
        of text. There's a division of into two forms: those in large pieces of
        inline text (paragraphs) with occasional embedded elements, or short pieces
        in elements of various structured. The document as a whole, is a mix of
        degrees of these two.

        This trieds to serve both purposes. Other visitor hooks toggle one of
        the following bits to get what is required:

        - **capture_text**, tells wether to concatenate the text onto the current
          context; this is usually used together with
        - **skip_content**, which will stop visit_Text from doing anything further.
          Otherwise
        - **tab_content** is one last bit that tells to either write indented
          blocks (_write_indented) or tabbed blocks (_write_tabbed).
        """
        text = node.astext()
        #encoded = self.encode(text)
        #if self.in_mailto and self.settings.cloak_email_addresses:
        #    encoded = self.cloak_email(encoded)
        if self.capture_text:
            captured = getattr(self.context, self.capture_text, '')
            setattr(self.context, self.capture_text, text)
        lines = text.split('\n') # XXX: unix
        if not self.skip_content:
            if self.tab_content:
                self._write_tabbed(*lines)
            else:
                self._write_indented(*lines)
    def depart_Text(self, node):
        pass

    def visit_title(self, node):
        previous_tree = self.context.tree
        if previous_tree and previous_tree[-1].tagname == 'topic':
            if not self.block_level:
                self._assure_newblock()
            self.sub_tree(node)
            self.visit_field_name(node)
        else:
            self.capture_text = 'title'
            self.sub_tree(node)
            #if previous_tree:
            #    self._assure_emptyline()
            #    self._write_newline()
            #    #self._assure_newblock()
        self.context.increment('index')
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
            self._write_indented( self.adornment * len(text) )
        self._assure_emptyline()

    def visit_subtitle(self, node):
        #self.debugprint(self.context)
        self.sub_tree(node)
        self.capture_text = 'subtitle'
        in_sidebar = self.in_tag('sidebar', '*')
        assert not in_sidebar, "TODO"
        assert not self.subtitle_adornment, node
        self.subtitle_adornment = self.get_new_section_adornment()
    def depart_subtitle(self, node):
        self.pop_tree()
        self.capture_text = None
        text = self.context.subtitle
        self._assure_emptyline()
        self._write_indented( self.subtitle_adornment  * len(text))
        self._assure_emptyline()
        del self.context.subtitle

    def visit_section(self, node):
        #self.debugprint(self.context)
        self.sub_tree(node)
        if not self.block_level:
            self._assure_newblock()
        self.context.increment('index')
        self.context.index = 0
        self.doclevel += 1
        self.set_title_adornment()
    def depart_section(self, node):
        self.pop_tree()
        self._assure_emptyline()
        del self.context.index
        self.doclevel -= 1

    def visit_paragraph(self, node):
        #self.debugprint(self.context)
        self.sub_tree(node)
        if not self.block_level:
            self._assure_newblock()
        self.context.increment('index')
        self.context.index = 0
    def depart_paragraph(self, node):
        self._assure_newblock()
        del self.context.index
        self.pop_tree()

    # Inline
    def visit_inline(self, node):
        #self.debugprint(self.context)
        self.sub_tree(node)
        self.context.increment('index')
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
            # XXX: use first super-role, after name is retrieved
            if len(inherit) > 1:
                classes.extend(inherit[1:])
            inherit = inherit[:1]
        role = self.add_role(name, " ".join(inherit), {'class': classes})
        self._write_indented(':%s:`' % role)
    def depart_inline(self, node):
        self.pop_tree()
        self._write_indented('`')

    def _visit_simple_inline(self, klass, decoration, node):
        if node.get('classes'):
            if klass:
                node['classes'].append(klass)
            self.visit_inline(node)
        else:
            self.sub_tree(node)
            self.context.increment('index')
            #self._write_indented(decoration)
            self.body.append(decoration)

    def _depart_simple_inline(self, klass, decoration, node):
        if node.get('classes'):
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
        #self.debugprint(self.context)
        self.sub_tree(node)
        self.context.increment('index')
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
        self.context.increment('index')
        self.context.index = 0
#        self.tab_content = ( 14, ) # indent into two cols, first is 14
        #self.context.indent += 5 * INDENT
    def depart_option_list(self, node):
        self.pop_tree()
        del self.context.index
        #del self.context.indent
        self.tab_content = None
        self._assure_emptyline()

    def visit_option_list_item(self):
        pass
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
        self.context.increment('index')
        if not self.root and self.in_tag('figure', '*'):
            pass
        else:
            if 'name' in node:
                pass
            elif 'refuri' in node:
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
            if 'name' in node:
                self.body.append('_')
            elif 'refuri' in node:
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
        self.context.increment('index')
        if 'auto' in node.attributes:
            self.skip_content = True
            self.capture_text = 'footnote_reference'
        else:
            self._write_indented('[')
    def depart_footnote_reference(self, node):
        if 'auto' in node.attributes:
            assert self.context.footnote_reference, self.context
            self.skip_content = False
            if self.context.footnote_reference.isdigit():
                self._write_indented('[#]_')
            else:
                self._write_indented('[*]_')
            del self.context.footnote_reference
        else:
            self.body.append(']_ ')
        self.pop_tree()

    def visit_substitution_definition(self, node):
        self.sub_tree(node)
        self.context.increment('index')
        self._assure_newblock()
        self.skip_content = True
        #TODO: unicode
        directive = 'replace'
        value = node.children[0]
        if value.tagname == '#text':
            node.rawsource = None
            if node.rawsource:
                value = node.rawsource.split('::')[1].lstrip()
            else:
                try:
                    value.decode('ascii')
                except UnicodeEncodeError, e:
                    directive = 'unicode'
                    assert len(value) == 1
                    value = str(hex(ord(value)))
                    #value = 'U+'+value[2:]
        elif value.tagname == 'image':
            directive = 'image'
            value = value.attributes['uri']
        self.body.append('.. |%s| %s:: ' % ( node['names'][0], directive ))
        self.body.append(value)

    def depart_substitution_definition(self, node):
        self.skip_content = False
        self.pop_tree()
        self._write_newline()

    def visit_citation_reference(self, node):
        self.sub_tree(node)
        self.context.increment('index')
        self.body.append('[')
    def depart_citation_reference(self, node):
        self.pop_tree()
        self.body.append(']_ ')

    def visit_target(self, node):
        """
        - with anonymous and ids: lost id/name and got number id and refuri or refid; same as:
        - with refid: block target, added its own id to endpoint, changed its id to refid
        - with refuri: block target, got a refuri back for adding an id to a below target

        Anything may be an endpoint, for most blocklevels this means the target
        created an id on the below block, to which gets a refid.
        But targets may be receiving id/names too, multiple targets even.
        Then each target has the refid of the lowest target that points
        elsewhere, the endpoint target.

        To retrieve their id/names they have go to the endpoint. The endpoint
        targets have forms:

        - with ids and names and refid: inbound link
        - with ids and names and refuri: outbound link

        Links do not add ids/names to their target. This means the following
        never have any additional ids/names?

        - with ids and names: inline target

        """
        self.sub_tree(node)
        names = node.get('names')
        ids = node.get('ids')
        refuri = node.get('refuri')
        refid = node.get('refid')
        anonymous = node.get('anonymous', 0)
        self.context.increment('index')

        if anonymous and ids: # anonymous
            self._write_indented('.. __:')
        elif ids and names and refid: # inbound link
            self._write_indented('.. _')
        elif ids and names and refuri: # outbound link
            self._write_indented('.. _')
        elif ids and names: # inline targets
            self._write_indented('.. _`')
        elif refid: # block targets I
            # perhaps should look up the id, but can use refid thats is the same
            self._write_indented('.. _')
        elif refuri: # block targets II
            pass # FIXME: need to lookup the id here..
        else:
            assert False, node

        if refuri or refid:
            if not self.block_level:
                self._assure_newblock()
        if names:
            self.body.append(names[0])
            self.body.append(": ")
        elif refuri:
            # XXX: what about multiple names?
            if 'names' in node and node['names']:
                self._write_indented("%s: %s" % (node['names'][0],
                    refuri))
            else:
                self._write_indented("`")
        elif refid:
            if 'names' in node and node['names']:
                if refid:
                    self._write_indented("%s: `%s`_" % (node['names'][0], refid))
                else:
                    assert False, node
                    self._write_indented("%s: %s_" % (node['names'][0], names[0]))
            else:
                self._write_indented("`")
        else:
            self._write_indented('_`')
    def depart_target(self, node):
        self.pop_tree()
        if 'refuri' not in node or not node['refuri']:
            pass
        if not 'refname' in node and not 'names' in node:
            if 'refid' not in node or not node['refid']:
                self._write_indented('`')
        self._assure_newblock()

    def visit_title_reference(self, node):
        self.sub_tree(node)
        self.context.increment('index')
        self._write_indented('`')
    def depart_title_reference(self, node):
        self._write_indented('`')
        self.pop_tree()

    def visit_footnote(self, node):
        self.sub_tree(node)
        if not self.block_level:
            self._assure_newblock()
        self.context.increment('index')
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
        p = node.parent
        if p.tagname == 'footnote' and 'auto' in p.attributes:
            self.skip_content = True
    def depart_label(self, node):
        p = node.parent
        if p.tagname == 'footnote':
            if self.skip_content:
                #self.debugprint(node)
                self.skip_content = False
            else:
                self.body.append("] ")
        elif self.in_tag('citation'):
            self.body.append('] ')

    # Images
    def visit_image(self, node):
        if self.in_tag('substitution_definition', '*'):
            return
        self.sub_tree(node)
        self.context.increment('index')
        if self.in_tag('figure', '*'):
            self.body.append(node['uri'])
            self._write_newline()
        else:
            self._assure_newblock()
            self._write_directive('image', node['uri'])
    def depart_image(self, node):
        if self.in_tag('substitution_definition', '*'):
            return
        self.pop_tree()

    def visit_figure(self, node):
        self.sub_tree(node)
        self.context.increment('index')
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
        if not self.block_level:
            self._assure_newblock()
        self.sub_tree(node)
        if node.attributes['xml:space'] == "preserve":
            self.preserve_ws = True
        self.context.increment('index')
        self._write_indented('.. ')
        self.context.indent += INDENT
    def depart_comment(self, node):
        self.pop_tree()
        self._assure_emptyline()
        del self.context.indent
        self.preserve_ws = False

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
        if 'classes' in node:
            if 'epigraph' in node.attributes['classes']:
                self.visit_directive(node, name='epigraph')
                return
        self.sub_tree(node)
        self._assure_newblock()
        self.context.increment('index')
        self.context.index = 0
        self.context.indent += '  '
    def depart_block_quote(self, node):
        if 'classes' in node:
            if 'epigraph' in node.attributes['classes']:
                self.depart_directive(node, name='epigraph')
                return
        self.pop_tree()
        del self.context.index
        del self.context.indent

    def visit_literal_block(self, node):
        pre = node.get('xml:space') #is always set?
        # look for non-text subnodes
        def cond(node):
            if node.tagname != '#text':#not isinstance(node, nodes.Text):
                return True
        nottext = node.traverse(condition=cond, include_self=False)
        parsed = len(nottext) > 0
        self.context.parsed = parsed
        x, y, lastchar = self.last_string(1)
        lastc = lastchar == ':'
        if not parsed and lastc:
            self.insert(x, y, ':')
        else:
            self._assure_newblock()
        self.sub_tree(node)
        self.context.increment('index')
        self.context.index = 0
        if not lastc:
            if parsed:
                self._write_directive('parsed-literal')
            else:
                self._write_indented(':: ')
        self._write_newline()
        # xxx: long winded way to detect quoted literal blocks
        lines = [ l.strip() for l in node.astext().strip().split('\n') if l.strip() ]
        quoted = [ l for l in lines if l[0] in quote_chars ]
        node.quoted = len(quoted) == len(lines)
        if not node.quoted:
            self.context.indent += '   '
        self._write_newline()
        #self._assure_newblock()
        self.preserve_ws = True
    def depart_literal_block(self, node):
        self.pop_tree()
        self._assure_newblock()
        del self.context.index
        if not node.quoted:
            del self.context.indent
        self.preserve_ws = False
        self.context.parsed

    # XXX: what can lineblock contain
    def visit_line_block(self, node):
        self.sub_tree(node)
        if not self.block_level:
            self._assure_newblock()
        self.context.increment('index')
        #self._assure_emptyline(2)
        self.context.index = 0
    def depart_line_block(self, node):
        del self.context.index
        self.pop_tree()
        self._assure_newblock()
        self._assure_emptyline()

    def visit_line(self, node):
        self.sub_tree(node)
        self.context.increment('index')
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
        self.context.increment('index')
        self.body.append(u'%s\n\n' %node.rawsource)
        self.indented = 0
    depart_transition = _pass_visit

    visit_problematic = _pass_visit
    depart_problematic = _pass_visit

    # Lists
    def visit_enumerated_list(self, node):
        #self.debugprint(node)
        self.sub_tree(node)
        if not self.block_level or self.context.index:
            self._assure_newblock()
        self.context.increment('index')
        self.context.index = 0
        if 'start' in node:
           self.context.offset = node.attributes['start']
        if 'suffix' in node:
            self.context.enumsuffix = node.attributes['suffix']
        self.context.enumtype = node.attributes['enumtype']
        self.context.counter = 0
    def depart_enumerated_list(self, node):
        self.pop_tree()
        if 'start' in node:
            self.context.offset
        del self.context.index
        del self.context.enumtype
        del self.context.counter
        #self._assure_newblock()

    def visit_bullet_list(self, node):
        #self.debugprint(node)
        self.sub_tree(node)
        if not self.block_level:
            self._assure_newblock()
        self.context.increment('index')
        self.context.index = 0
        self.context.bullet = node.attributes['bullet']
        self.context.counter = 0
    def depart_bullet_list(self, node):
        del self.context.index
        del self.context.bullet
        self.pop_tree()

    def visit_list_item(self, node):
        # for enumerate only but anyway:
        self.context.replace('counter', self.context.counter+1)
        self.sub_tree(node)
        self.context.increment('index') # increment to new item at parent level
        self.context.index = 0
        enum_index = self.context.counter + ( self.context.offset and self.context.offset-1 or 0)
        is_bullet = self.in_tag('bullet_list', 1)
        #assert is_bullet or self.in_tag('enumerated_list', 1), \
        #        "Illegal container for %s %s, %s" % (self.in_tag(), self.path, self.in_tag(None, 1))
        #self.debugprint(,node)
        if is_bullet:
            bullet_instance = u'%s ' % self.context.bullet
            self._write_indented(bullet_instance)
            lil = len(bullet_instance)
        else:
            enum_instance = u'%s%s ' % (
                    self.enumeration_symbol[self.context.enumtype](enum_index),
                    self.context.enumsuffix or ''
                )
            self._write_indented(enum_instance)
            lil = len(enum_instance)
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
        self.context.increment('index')
        #self.expect('definition_list_item')
        self.context.index = 0
    def depart_definition_list(self, node):
        self.pop_tree()
        del self.context.index

    def visit_definition_list_item(self, node):
        self.sub_tree(node)
        #self.expect('term', 'classifier', 'definition')
        self.context.increment('index')
        self.context.index = 0
    def depart_definition_list_item(self, node):
        self.pop_tree()
        self._assure_emptyline()
        del self.context.index

    def visit_term(self, node):
        self.sub_tree(node)
        self.context.increment('index')
    def depart_term(self, node):
        self._assure_emptyline()
        self.pop_tree()

    visit_classifier = _pass_visit
    depart_classifier = _pass_visit

    def visit_definition(self, node):
        self.sub_tree(node)
        self.context.increment('index')
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
        self.context.increment('index')
        self.context.index = 0
    def depart_field_list(self, node):
        self.pop_tree()
        del self.context.index
        self._assure_emptyline()

    def visit_field(self, node):
        self.sub_tree(node)
        self.context.increment('index')
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
        """
        The problem for tables is, how to write embedded structures.
        E.g. text would need to be written to its own context, one per cell.
        And then it can get wrapping, resizing added borders and write it in one go. Ugh.

        See option_list for start with tabbed writing.
        """
        self.debugprint(node)
    depart_table = _pass_visit

    def visit_colspec(self, node):
        self.debugprint(node)
    depart_colspec = _pass_visit

    def visit_caption(self, node):
        self.sub_tree(node)
        # first paragraph in figure
        self._assure_newblock()
        self.context.increment('index')
    def depart_caption(self, node):
        self.pop_tree()

    def visit_legend(self, node):
        # other paragraphs in figure
        self.sub_tree(node)
        self._assure_newblock()
        self.context.increment('index')
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
            self.context.increment('index')
            self._write_indented(':%s: ' % (cn.title())) # XXX
            self.context.index = 0
            self.context.indent += '  '
            return
        elif cn in self.admonition_fields:
            self.context.increment('index')
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
        self.context.increment('index')
        self.context.index = 0
        if not name:
            name = classname(node)
        self._write_directive(name)
        self.context.indent += '   '
        # TODO: options
        # TODO: arguments/classes
    def depart_directive(self, node, name=None):
        self.pop_tree()
        del self.context.indent
        del self.context.index

    def debugprint(self, node):
        self.body.append("[du.rst:XXX:%s %r %r %r %s]" % (node.tagname, self.context.index,
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
        '''Initialise _defaults and _stack, but avoid calling self.__setattr__'''
        if defaults is None:
            self.replace('_defaults', {})
        else:
            self.set('_defaults', dict(defaults))
        self.set( '_stack', {} )

    def __getattr__(self, name):
        '''Return last value of name in stack, or default.'''
        if name in self._stack:
            return self._stack[name][-1]
        if name in self._defaults:
            return self._defaults[name]
        raise AttributeError

    def append(self, name, value):
        """
        Append item to a list property, increasing stack level
        """
        l = list(getattr(self, name))
        l.append(value)
        setattr(self, name, l)

    def set(self, name, value):
        object.__setattr__(self, name, value)

    def replace(self, name, value):
        "do not increase stack level"
        assert name in self._stack, name
        values = self._stack[name][:-1]
        self._stack[name] = values + [value]
        return value

    def increment(self, name):
        old = self.current(name)
        self.replace(name, self.current(name) + 1)
        return self.current(name)

    def current(self, name):
        try:
            assert name in self._stack, (name, self._stack)
            return self._stack[name][-1]
        except:
            print 'ContextStack.curront no key', name, self._stack
            return 0

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
        if not self._stack[name] and not isinstance(self._stack[name], int):
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

class RstDocumentTranslator(AbstractTranslator):
    """
    Main document visitor. This defers to the other subtranslators.
    """
    pass

class RstSectionTranslator(AbstractTranslator):
    """
    Subtranslaters for sections. Sections may contain subsections.
    """
    pass

class RstTableTranslator(AbstractTranslator):
    """
    Tables may contain anything a section can but not subsections.
    """
    pass


def classname(obj):
    return obj.__class__.__name__



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
# References, targets are broken.
# And other bugs: starting with least complex:
'var/test-rst.5.inline-5.rst',
#'var/test-rst.5.inline-6.rst',
#'var/test-rst.5.inline-7.rst',
#'var/test-rst.5.inline-3.rst',
#'var/test-rst.24.references.rst',
#'var/test-rst.5.inline-4.rst',
#'var/test-rst.1.document-5.full-rst-demo.rst',
# interesting for later:
#'var/test-rst.2.title-1.rst',
#'var/test-rst.1.document-7.rst',
#'var/test-rst.6.bullet-list-2.rst',
# look at field-lists, only minimal newlines required:
#'var/test-rst.8.field-list-3.rst',
#'var/test-rst.8.field-list-4.rst',
        ]
        #TEST_DOC = filter(os.path.getsize,
        #        glob.glob(os.path.join(PROJ_ROOT, 'var', '*.rst')))
        TEST_DOC.sort()

        for doc in TEST_DOC:
            util.print_compare_writer(doc, writer_class=Writer, max_width=max_width)

