import roman, re
from docutils import frontend, parsers, nodes
import docutils.statemachine
from docutils.statemachine import StateMachineWS, StateWS
from docutils.utils import escape2null, unescape
from docutils.parsers.rst import languages, states, tableparser


class Parser(parsers.Parser):

    """Atlassian Wiki markup parser."""

    supported = ()
    """Aliases this parser supports."""

    settings_spec = (
        'Atlassian Wiki Parser Options',
        None,
        (
         ('Set number of spaces for tab expansion (default 8).',
          ['--tab-width'],
          {'metavar': '<width>', 'type': 'int', 'default': 8,
           'validator': frontend.validate_nonnegative_int}),
          ))

    config_section = 'atlassian parser'
    config_section_dependencies = ('parsers',)

    def __init__(self, rfc2822=None, inliner=None):
        if rfc2822:
            self.initial_state = 'RFC2822Body'
        else:
            self.initial_state = 'Body'
        self.state_classes = state_classes
        self.inliner = inliner

    def parse(self, inputstring, document):
        """Parse `inputstring` and populate `document`, a document tree."""
        self.setup_parse(inputstring, document)
        self.statemachine = AtlassianStateMachine(
              state_classes=self.state_classes,
              initial_state=self.initial_state,
              debug=document.reporter.debug_flag)
        inputlines = docutils.statemachine.string2lines(
              inputstring, tab_width=document.settings.tab_width,
              convert_whitespace=1)
        #assert document.settings.input_encoding == 'unicode'
        assert isinstance(inputstring, unicode)
        self.statemachine.run(inputlines, document, inliner=self.inliner)
        self.finish_parse()


class Inliner:
    def init_customizations(self, settings):
        pass

    def parse(self, text, lineno, memo, parent):
        # Needs to be refactored for nested inline markup.
        # Add nested_parse() method?
        """
        Return 2 lists: nodes (text and inline elements), and system_messages.

        Using `self.patterns.initial`, a pattern which matches start-strings
        (emphasis, strong, interpreted, phrase reference, literal,
        substitution reference, and inline target) and complete constructs
        (simple reference, footnote reference), search for a candidate.  When
        one is found, check for validity (e.g., not a quoted '*' character).
        If valid, search for the corresponding end string if applicable, and
        check it for validity.  If not found or invalid, generate a warning
        and ignore the start-string.  Implicit inline markup (e.g. standalone
        URIs) is found last.
        """
        self.reporter = memo.reporter
        self.document = memo.document
        self.language = memo.language
        self.parent = parent
        pattern_search = self.patterns.initial.search
        dispatch = self.dispatch
        remaining = escape2null(text)
        processed = []
        unprocessed = []
        messages = []
        while remaining:
            match = pattern_search(remaining)
            if match:
                groups = match.groupdict()
                method = dispatch[groups['start'] or groups['backquote']
                                  or groups['refend'] or groups['fnend']]
                before, inlines, remaining, sysmessages = method(self, match,
                                                                 lineno)
                unprocessed.append(before)
                messages += sysmessages
                if inlines:
                    #processed += self.implicit_inline(''.join(unprocessed),
                    #                                  lineno)
                    processed += inlines
                    unprocessed = []
            else:
                break
        remaining = ''.join(unprocessed) + remaining
        #if remaining:
        #    processed += self.implicit_inline(remaining, lineno)
        return processed, messages
    
    openers = u'\'"([{<\u2018\u201c\xab\u00a1\u00bf' # see quoted_start below
    closers = u'\'")]}>\u2019\u201d\xbb!?'
    unicode_delimiters = u'\u2010\u2011\u2012\u2013\u2014\u00a0'
    start_string_prefix = (u'((?<=^)|(?<=[-/: \\n\u2019%s%s]))'
                           % (re.escape(unicode_delimiters),
                              re.escape(openers)))
    end_string_suffix = (r'((?=$)|(?=[-/:.,; \n\x00%s%s]))'
                         % (re.escape(unicode_delimiters),
                            re.escape(closers)))
    non_whitespace_escape_before = r'(?<![ \n\x00])'
    non_whitespace_after = r'(?![ \n])'
    # Alphanumerics with isolated internal [-._+:] chars (i.e. not 2 together):
    simplename = r'(?:(?!_)\w)+(?:[-._+:](?:(?!_)\w)+)*'

    parts = ('initial_inline', start_string_prefix, '',
             [('start', '', non_whitespace_after,  # simple start-strings
               [r'\*',                # strong
                r'_',                 # emphasis 
                r'\?\?',              # citation
                r'-',                 # strikethrough
                r'\+',                 # underlined
                r'\^',                 # superscript
                r'~',                 # subscript
                r'{',                 # explicit inline markup
                ]
               ),
              ('whole', '', end_string_suffix, # whole constructs
               [# reference name & end-string
               # r'(?P<refname>%s)(?P<refend>__?)' % simplename,
               # ('footnotelabel', r'\[', r'(?P<fnend>\]_)',
               #  [r'[0-9]+',               # manually numbered
               #   r'\#(%s)?' % simplename, # auto-numbered (w/ label?)
               #   r'\*',                   # auto-symbol
               #   r'(?P<citationlabel>%s)' % simplename] # citation reference
               #  )
               ]
               ),
              ('backquote',             # interpreted text or phrase reference
               '(?P<role>(:%s:)?)' % simplename, # optional role
               non_whitespace_after,
               ['`(?!`)']               # but not literal
               )
              ]
             )
    patterns = states.Struct(
          initial=states.build_regexp(parts),
          explicit_inline=re.compile(non_whitespace_escape_before
                            + r'({)' + end_string_suffix),
      )

    def quoted_start(self, match):
        """Return 1 if inline markup start-string is 'quoted', 0 if not."""
        string = match.string
        start = match.start()
        end = match.end()
        if start == 0:                  # start-string at beginning of text
            return 0
        prestart = string[start - 1]
        try:
            poststart = string[end]
            if self.openers.index(prestart) \
                  == self.closers.index(poststart):   # quoted
                return 1
        except IndexError:              # start-string at end of text
            return 1
        except ValueError:              # not quoted
            pass
        return 0

    def inline_obj(self, match, lineno, end_pattern, nodeclass,
                   restore_backslashes=0):
        string = match.string
        matchstart = match.start('start')
        matchend = match.end('start')
        if self.quoted_start(match):
            return (string[:matchend], [], string[matchend:], [], '')
        endmatch = end_pattern.search(string[matchend:])
        if endmatch and endmatch.start(1):  # 1 or more chars
            text = unescape(endmatch.string[:endmatch.start(1)],
                            restore_backslashes)
            textend = matchend + endmatch.end(1)
            rawsource = unescape(string[matchstart:textend], 1)
            return (string[:matchstart], [nodeclass(rawsource, text)],
                    string[textend:], [], endmatch.group(1))
        msg = self.reporter.warning(
              'Inline %s start-string without end-string.'
              % nodeclass.__name__, line=lineno)
        text = unescape(string[matchstart:matchend], 1)
        rawsource = unescape(string[matchstart:matchend], 1)
        prb = self.problematic(text, rawsource, msg)
        return string[:matchstart], [prb], string[matchend:], [msg], ''

    def problematic(self, text, rawsource, message):
        msgid = self.document.set_id(message, self.parent)
        problematic = nodes.problematic(rawsource, text, refid=msgid)
        prbid = self.document.set_id(problematic)
        message.add_backref(prbid)
        return problematic

    def emphasis(self, match, lineno):
        before, inlines, remaining, sysmessages, endstring = self.inline_obj(
              match, lineno, self.patterns.emphasis, nodes.emphasis)
        return before, inlines, remaining, sysmessages

    def strong(self, match, lineno):
        before, inlines, remaining, sysmessages, endstring = self.inline_obj(
              match, lineno, self.patterns.strong, nodes.strong)
        return before, inlines, remaining, sysmessages

    def explicit_inline(self, match, lineno):
        before, inlines, remaining, sysmessages, endstring = self.inline_obj(
              match, lineno, self.patterns.explicit_inline, nodes.strong)
        return before, inlines, remaining, sysmessages

    dispatch = {
            '_': emphasis,
            #'**': strong,
            #'`': interpreted_or_phrase_ref,
            #'``': literal,
            #'_`': inline_internal_target,
            #']_': footnote_reference,
            #'|': substitution_reference,
            #'_': reference,
            '{': explicit_inline
        }


class AtlassianStateMachine(StateMachineWS):

    """
    Atlassian Wiki's master StateMachine.

    The entry point to Atlassian Wiki parsing is the `run()` method.
    """

    def run(self, input_lines, document, input_offset=0, match_titles=1,
            inliner=None):
        """
        Parse `input_lines` and modify the `document` node in place.

        Extend `StateMachineWS.run()`: set up parse-global data and
        run the StateMachine.
        """
        self.language = languages.get_language(
            document.settings.language_code)
        self.match_titles = match_titles
        if inliner is None:
            inliner = Inliner()
        inliner.init_customizations(document.settings)
        self.memo = states.Struct(document=document,
                           reporter=document.reporter,
                           language=self.language,
                           title_styles=[],
                           section_level=0,
                           section_bubble_up_kludge=0,
                           inliner=inliner)
        self.document = document
        self.attach_observer(document.note_source)
        self.reporter = self.memo.reporter
        self.node = document
        self.debug = True
#        print "\n| ".join(input_lines)
#        assert sys.stderr.encoding
#        assert document.settings.input_encoding == 'unicode'
#        assert document.settings.output_encoding == 'unicode'
#        assert document.settings.error_encoding == 'unicode'
#        assert document.settings.error_encoding_error_handler == 'replace'
# FIXME: why is stderr encoding not set?
        results = StateMachineWS.run(self, input_lines, input_offset,
                                     input_source=document['source'])
        assert results == [], 'AtlassianStateMachine.run() results should be empty!'
        self.node = self.memo = None    # remove unneeded references



class AtlassianState(StateWS):

    """
    Atlassian Wiki State superclass.

    Contains methods used by all State subclasses.
    """

    nested_sm = None#NestedStateMachine
    nested_sm_cache = []

    def __init__(self, state_machine, debug=0):
        self.nested_sm_kwargs = {'state_classes': state_classes,
                                 'initial_state': 'Body'}
        StateWS.__init__(self, state_machine, debug)

    def runtime_init(self):
        StateWS.runtime_init(self)
        memo = self.state_machine.memo
        self.memo = memo
        self.reporter = memo.reporter
        self.inliner = memo.inliner
        self.document = memo.document
        self.parent = self.state_machine.node
        # enable the reporter to determine source and source-line
        if not hasattr(self.reporter, 'locator'):
            self.reporter.locator = self.state_machine.get_source_and_line
            # print "adding locator to reporter", self.state_machine.input_offset

    def goto_line(self, abs_line_offset):
        """
        Jump to input line `abs_line_offset`, ignoring jumps past the end.
        """
        try:
            self.state_machine.goto_line(abs_line_offset)
        except EOFError:
            pass

    def no_match(self, context, transitions):
        """
        Override `StateWS.no_match` to generate a system message.

        This code should never be run.
        """
        src, srcline = self.state_machine.get_source_and_line()
        self.reporter.severe(
            'Internal error: no transition pattern match.  State: "%s"; '
            'transitions: %s; context: %s; current line: %r.'
            % (self.__class__.__name__, transitions, context,
               self.state_machine.line),
            source=src, line=srcline)
        return context, None, []

    def bof(self, context):
        """Called at beginning of file."""
        return [], []

    def paragraph(self, lines, lineno):
        """
        Return a list (paragraph & messages)
        """
        text = '\n'.join(lines).rstrip()
        textnodes, messages = self.inline_text(text, lineno)
        p = nodes.paragraph(text, '', *textnodes)
        p.source, p.line = self.state_machine.get_source_and_line(lineno)
        return [p] + messages, False

    def inline_text(self, text, lineno):
        """
        Return 2 lists: nodes (text and inline elements), and system_messages.
        """
        return self.inliner.parse(text, lineno, self.memo, self.parent)


class Body(AtlassianState):

    """
    Generic classifier of the first line of a block.
    """

    double_width_pad_char = tableparser.TableParser.double_width_pad_char
    """Padding character for East Asian double-width text."""

#    enum = states.Struct()
#    """Enumerated list parsing information."""
#
#    enum.formatinfo = {
#          'parens': states.Struct(prefix='(', suffix=')', start=1, end=-1),
#          'rparen': states.Struct(prefix='', suffix=')', start=0, end=-1),
#          'period': states.Struct(prefix='', suffix='.', start=0, end=-1)}
#    enum.formats = enum.formatinfo.keys()
#    enum.sequences = ['arabic', 'loweralpha', 'upperalpha',
#                      'lowerroman', 'upperroman'] # ORDERED!
#    enum.sequencepats = {'arabic': '[0-9]+',
#                         'loweralpha': '[a-z]',
#                         'upperalpha': '[A-Z]',
#                         'lowerroman': '[ivxlcdm]+',
#                         'upperroman': '[IVXLCDM]+',}
#    enum.converters = {'arabic': int,
#                       'loweralpha': states._loweralpha_to_int,
#                       'upperalpha': states._upperalpha_to_int,
#                       'lowerroman': states._lowerroman_to_int,
#                       'upperroman': roman.fromRoman}
#
#    enum.sequenceregexps = {}
#    for sequence in enum.sequences:
#        enum.sequenceregexps[sequence] = re.compile(
#              enum.sequencepats[sequence] + '$')

    grid_table_top_pat = re.compile(r'\+-[-+]+-\+ *$')
    """Matches the top (& bottom) of a full table)."""

    simple_table_top_pat = re.compile('=+( +=+)+ *$')
    """Matches the top of a simple table."""

    simple_table_border_pat = re.compile('=+[ =]*$')
    """Matches the bottom & header bottom of a simple table."""

    pats = {}
    """Fragments of patterns used by transitions."""

    pats['nonalphanum7bit'] = '[!-/:-@[-`{-~]'
#    pats['alpha'] = '[a-zA-Z]'
#    pats['alphanum'] = '[a-zA-Z0-9]'
#    pats['alphanumplus'] = '[a-zA-Z0-9_-]'
#    pats['enum'] = ('(%(arabic)s|%(loweralpha)s|%(upperalpha)s|%(lowerroman)s'
#                    '|%(upperroman)s|#)' % enum.sequencepats)
#    pats['optname'] = '%(alphanum)s%(alphanumplus)s*' % pats
#    # @@@ Loosen up the pattern?  Allow Unicode?
#    pats['optarg'] = '(%(alpha)s%(alphanumplus)s*|<[^<>]+>)' % pats
#    pats['shortopt'] = r'(-|\+)%(alphanum)s( ?%(optarg)s)?' % pats
#    pats['longopt'] = r'(--|/)%(optname)s([ =]%(optarg)s)?' % pats
#    pats['option'] = r'(%(shortopt)s|%(longopt)s)' % pats

#    for format in enum.formats:
#        pats[format] = '(?P<%s>%s%s%s)' % (
#              format, re.escape(enum.formatinfo[format].prefix),
#              pats['enum'], re.escape(enum.formatinfo[format].suffix))

    patterns = {
          'explicit_markup': r'\.\.( +|$)',
          'line': r'(%(nonalphanum7bit)s)\1* *$' % pats,
          'text': r''}
    initial_transitions = (
          'explicit_markup',
          'text'
      )

    def explicit_markup(self, match, context, next_state):
        """Footnotes, hyperlink targets, directives, comments."""
        nodelist, blank_finish = self.explicit_construct(match)
        self.parent += nodelist
        self.explicit_list(blank_finish)
        return [], next_state, []

    def text(self, match, context, next_state):
        """Titles, definition lists, paragraphs."""
        #print 'body text', match, context, next_state
        return [match.string], 'Text', []



class RFC2822Body(Body):

    """
    RFC2822 headers are only valid as the first constructs in documents.  As
    soon as anything else appears, the `Body` state should take over.
    """

    patterns = Body.patterns.copy()     # can't modify the original
    patterns['rfc2822'] = r'[!-9;-~]+:( +|$)'
    initial_transitions = [(name, 'Body')
                           for name in Body.initial_transitions]
    initial_transitions.insert(-1, ('rfc2822', 'Body')) # just before 'text'

    def rfc2822(self, match, context, next_state):
        """RFC2822-style field list item."""
        fieldlist = nodes.field_list(classes=['rfc2822'])
        self.parent += fieldlist
        field, blank_finish = self.rfc2822_field(match)
        fieldlist += field
        offset = self.state_machine.line_offset + 1   # next line
        newline_offset, blank_finish = self.nested_list_parse(
              self.state_machine.input_lines[offset:],
              input_offset=self.state_machine.abs_line_offset() + 1,
              node=fieldlist, initial_state='RFC2822List',
              blank_finish=blank_finish)
        self.goto_line(newline_offset)
        if not blank_finish:
            self.parent += self.unindent_warning(
                  'RFC2822-style field list')
        return [], next_state, []

    def rfc2822_field(self, match):
        name = match.string[:match.string.find(':')]
        indented, indent, line_offset, blank_finish = \
              self.state_machine.get_first_known_indented(match.end(),
                                                          until_blank=1)
        fieldnode = nodes.field()
        fieldnode += nodes.field_name(name, name)
        fieldbody = nodes.field_body('\n'.join(indented))
        fieldnode += fieldbody
        if indented:
            self.nested_parse(indented, input_offset=line_offset,
                              node=fieldbody)
        return fieldnode, blank_finish


class Text(AtlassianState):

    patterns = {
            #    'underline': Body.patterns['line'],
                'text': r''}
    initial_transitions = [
            #('underline', 'Body'), 
            ('text', 'Body')
            ]

    def blank(self, match, context, next_state):
        """End of paragraph."""
        paragraph, literalnext = self.paragraph(
              context, self.state_machine.abs_line_number() - 1)
        self.parent += paragraph
        if literalnext:
            self.parent += self.literal_block()
        return [], 'Body', []

    def eof(self, context):
        if context:
            self.blank(None, context, None)
        return []

    def text(self, match, context, next_state):
        """Paragraph."""
        startline = self.state_machine.abs_line_number() - 1
        msg = None
        try:
            block = self.state_machine.get_text_block(flush_left=1)
        except statemachine.UnexpectedIndentationError, instance:
            block, src, srcline = instance.args
            msg = self.reporter.error('Unexpected indentation.',
                                      source=src, line=srcline)
        lines = context + list(block)
        paragraph, literalnext = self.paragraph(lines, startline)
        self.parent += paragraph
        self.parent += msg
        return [], next_state, []


state_classes = (
               Body, 
               #  RFC2822Body, 
                 Text,
                 #RFC2822List
                 )
"""Standard set of State classes used to start `AtlassianStateMachine`."""

