"""
A stripped version of the RSTStateMachine as a basis to experiment.

This parses a simple format of nested sections with titles and
paragraphs with strong or emphasized inline spans.

I'm trying to strip and scrap the rSt as I go, but it is hard to separate.
"""

import re

import docutils
from docutils import frontend, parsers, nodes
from docutils.nodes import fully_normalize_name as normalize_name
from docutils.statemachine import StateMachineWS, StateWS
from docutils.utils import escape2null, unescape
from docutils.parsers.rst import languages
from docutils.parsers.rst.states import build_regexp, Struct



class Inliner:

    """
    Parse inline markup; call the `parse()` method.
    """

    def __init__(self):
        self.implicit_dispatch = [(self.patterns.uri, self.standalone_uri),]
        """List of (pattern, bound method) tuples, used by
        `self.implicit_inline`."""

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
                    processed += self.implicit_inline(''.join(unprocessed),
                                                      lineno)
                    processed += inlines
                    unprocessed = []
            else:
                break
        remaining = ''.join(unprocessed) + remaining
        if remaining:
            processed += self.implicit_inline(remaining, lineno)
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
    non_whitespace_before = r'(?<![ \n])'
    non_whitespace_escape_before = r'(?<![ \n\x00])'
    non_unescaped_whitespace_escape_before = r'(?<!(?<!\x00)[ \n\x00])'
    non_whitespace_after = r'(?![ \n])'
    # Alphanumerics with isolated internal [-._+:] chars (i.e. not 2 together):
    simplename = r'(?:(?!_)\w)+(?:[-._+:](?:(?!_)\w)+)*'
    # Valid URI characters (see RFC 2396 & RFC 2732);
    # final \x00 allows backslash escapes in URIs:
    uric = r"""[-_.!~*'()[\];/:@&=+$,%a-zA-Z0-9\x00]"""
    # Delimiter indicating the end of a URI (not part of the URI):
    uri_end_delim = r"""[>]"""
    # Last URI character; same as uric but no punctuation:
    urilast = r"""[_~*/=+a-zA-Z0-9]"""
    # End of a URI (either 'urilast' or 'uric followed by a
    # uri_end_delim'):
    uri_end = r"""(?:%(urilast)s|%(uric)s(?=%(uri_end_delim)s))""" % locals()
    emailc = r"""[-_!~*'{|}/#?^`&=+$%a-zA-Z0-9\x00]"""
    email_pattern = r"""
          %(emailc)s+(?:\.%(emailc)s+)*   # name
          (?<!\x00)@                      # at
          %(emailc)s+(?:\.%(emailc)s*)*   # host
          %(uri_end)s                     # final URI char
          """
    parts = ('initial_inline', start_string_prefix, '',
             [('start', '', non_whitespace_after,  # simple start-strings
               [r'\*\*',                # strong
                r'\*(?!\*)',            # emphasis but not strong
                r'``',                  # literal
                r'_`',                  # inline internal target
                r'\|(?!\|)']            # substitution reference
               ),
              ('whole', '', end_string_suffix, # whole constructs
               [# reference name & end-string
                r'(?P<refname>%s)(?P<refend>__?)' % simplename,
                ('footnotelabel', r'\[', r'(?P<fnend>\]_)',
                 [r'[0-9]+',               # manually numbered
                  r'\#(%s)?' % simplename, # auto-numbered (w/ label?)
                  r'\*',                   # auto-symbol
                  r'(?P<citationlabel>%s)' % simplename] # citation reference
                 )
                ]
               ),
              ('backquote',             # interpreted text or phrase reference
               '(?P<role>(:%s:)?)' % simplename, # optional role
               non_whitespace_after,
               ['`(?!`)']               # but not literal
               )
              ]
             )
    patterns = Struct(
          initial=build_regexp(parts),
          emphasis=re.compile(non_whitespace_escape_before
                              + r'(\*)' + end_string_suffix),
          strong=re.compile(non_whitespace_escape_before
                            + r'(\*\*)' + end_string_suffix),
          embedded_uri=re.compile(
              r"""
              (
                (?:[ \n]+|^)            # spaces or beginning of line/string
                <                       # open bracket
                %(non_whitespace_after)s
                ([^<>\x00]+)            # anything but angle brackets & nulls
                %(non_whitespace_before)s
                >                       # close bracket w/o whitespace before
              )
              $                         # end of string
              """ % locals(), re.VERBOSE),
          literal=re.compile(non_whitespace_before + '(``)'
                             + end_string_suffix),
          target=re.compile(non_whitespace_escape_before
                            + r'(`)' + end_string_suffix),
          substitution_ref=re.compile(non_whitespace_escape_before
                                      + r'(\|_{0,2})'
                                      + end_string_suffix),
          email=re.compile(email_pattern % locals() + '$', re.VERBOSE),
          uri=re.compile(
                (r"""
                %(start_string_prefix)s
                (?P<whole>
                  (?P<absolute>           # absolute URI
                    (?P<scheme>             # scheme (http, ftp, mailto)
                      [a-zA-Z][a-zA-Z0-9.+-]*
                    )
                    :
                    (
                      (                       # either:
                        (//?)?                  # hierarchical URI
                        %(uric)s*               # URI characters
                        %(uri_end)s             # final URI char
                      )
                      (                       # optional query
                        \?%(uric)s*
                        %(uri_end)s
                      )?
                      (                       # optional fragment
                        \#%(uric)s*
                        %(uri_end)s
                      )?
                    )
                  )
                |                       # *OR*
                  (?P<email>              # email address
                    """ + email_pattern + r"""
                  )
                )
                %(end_string_suffix)s
                """) % locals(), re.VERBOSE),
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

    def literal(self, match, lineno):
        before, inlines, remaining, sysmessages, endstring = self.inline_obj(
              match, lineno, self.patterns.literal, nodes.literal,
              restore_backslashes=1)
        return before, inlines, remaining, sysmessages

    def reference(self, match, lineno, anonymous=None):
        referencename = match.group('refname')
        refname = normalize_name(referencename)
        referencenode = nodes.reference(
            referencename + match.group('refend'), referencename,
            name=whitespace_normalize_name(referencename))
        if anonymous:
            referencenode['anonymous'] = 1
        else:
            referencenode['refname'] = refname
            self.document.note_refname(referencenode)
        string = match.string
        matchstart = match.start('whole')
        matchend = match.end('whole')
        return (string[:matchstart], [referencenode], string[matchend:], [])

    def anonymous_reference(self, match, lineno):
        return self.reference(match, lineno, anonymous=1)

    def standalone_uri(self, match, lineno):
        if (not match.group('scheme')
                or match.group('scheme').lower() in urischemes.schemes):
            if match.group('email'):
                addscheme = 'mailto:'
            else:
                addscheme = ''
            text = match.group('whole')
            unescaped = unescape(text, 0)
            return [nodes.reference(unescape(text, 1), unescaped,
                                    refuri=addscheme + unescaped)]
        else:                   # not a valid scheme
            raise MarkupMismatch

    def implicit_inline(self, text, lineno):
        """
        Check each of the patterns in `self.implicit_dispatch` for a match,
        and dispatch to the stored method for the pattern.  Recursively check
        the text before and after the match.  Return a list of `nodes.Text`
        and inline element nodes.
        """
        if not text:
            return []
        for pattern, method in self.implicit_dispatch:
            match = pattern.search(text)
            if match:
                try:
                    # Must recurse on strings before *and* after the match;
                    # there may be multiple patterns.
                    return (self.implicit_inline(text[:match.start()], lineno)
                            + method(match, lineno) +
                            self.implicit_inline(text[match.end():], lineno))
                except MarkupMismatch:
                    pass
        return [nodes.Text(unescape(text), rawsource=unescape(text, 1))]

    dispatch = {'*': emphasis,
                '**': strong,
                '``': literal,
                '_': reference,
                '__': anonymous_reference}



class SimpleParserStateMachine(StateMachineWS):

    """
    reStructuredText's master StateMachine.

    The entry point to reStructuredText parsing is the `run()` method.
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
        self.memo = Struct(document=document,
                           reporter=document.reporter,
                           language=self.language,
                           section_level=0,
                           inliner=inliner)
        self.document = document
        self.attach_observer(document.note_source)
        self.reporter = self.memo.reporter
        self.node = document
        results = StateMachineWS.run(self, input_lines, input_offset,
                                     input_source=document['source'])
        assert results == [], 'SimpleParserStateMachine.run() results should be empty!'
        self.node = self.memo = None    # remove unneeded references


class NestedStateMachine(StateMachineWS):

    """
    StateMachine run from within other StateMachine runs, to parse nested
    document structures.
    """

    def run(self, input_lines, input_offset, memo, node, match_titles=1):
        """
        Parse `input_lines` and populate a `docutils.nodes.document` instance.

        Extend `StateMachineWS.run()`: set up document-wide data.
        """
        self.match_titles = match_titles
        self.memo = memo
        self.document = memo.document
        self.attach_observer(self.document.note_source)
        self.reporter = memo.reporter
        self.language = memo.language
        self.node = node
        results = StateMachineWS.run(self, input_lines, input_offset)
        assert results == [], ('NestedStateMachine.run() results should be '
                               'empty!')
        return results


class Parser(parsers.Parser):

    """ Simple Markup experimentation. """

    settings_spec = (
        'Simple Markup Parser Options',
        None,
        (
         ('Set number of spaces for tab expansion (default 8).',
          ['--tab-width'],
          {'metavar': '<width>', 'type': 'int', 'default': 8,
           'validator': frontend.validate_nonnegative_int}),
          )
        )

    config_section = 'simplemuxdem parser'
    config_section_dependencies = ('parsers',)

    def __init__(self, inliner=None):
        self.initial_state = 'Body'
        self.state_classes = state_classes
        self.inliner = inliner

    def parse(self, inputstring, document):
        """Parse `inputstring` and populate `document`, a document tree."""
        self.setup_parse(inputstring, document)
        self.statemachine = SimpleParserStateMachine(
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


class SimpleParserState(StateWS):

    """
    Atlassian Wiki State superclass.

    Contains methods used by all State subclasses.
    """

    nested_sm = NestedStateMachine
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

    def nested_parse(self, block, input_offset, node, match_titles=0,
                     state_machine_class=None, state_machine_kwargs=None):
        """
        Create a new StateMachine rooted at `node` and run it over the input
        `block`.
        """
        use_default = 0
        if state_machine_class is None:
            state_machine_class = self.nested_sm
            use_default += 1
        if state_machine_kwargs is None:
            state_machine_kwargs = self.nested_sm_kwargs
            use_default += 1
        block_length = len(block)

        state_machine = None
        if use_default == 2:
            try:
                state_machine = self.nested_sm_cache.pop()
            except IndexError:
                pass
        if not state_machine:
            state_machine = state_machine_class(debug=self.debug,
                                                **state_machine_kwargs)
        state_machine.run(block, input_offset, memo=self.memo,
                          node=node, match_titles=match_titles)
        if use_default == 2:
            self.nested_sm_cache.append(state_machine)
        else:
            state_machine.unlink()
        new_offset = state_machine.abs_line_offset()
        # No `block.parent` implies disconnected -- lines aren't in sync:
        if block.parent and (len(block) - block_length) != 0:
            # Adjustment for block if modified in nested parse:
            self.state_machine.next_line(len(block) - block_length)
        return new_offset

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



class Body(SimpleParserState):

    """
    Generic classifier of the first line of a block.
    """

    enum = Struct()
    """Enumerated list parsing information."""

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

    pats = {}
    """Fragments of patterns used by transitions."""

    pats['nonalphanum7bit'] = '[!-/:-@[-`{-~]'

#    for format in enum.formats:
#        pats[format] = '(?P<%s>%s%s%s)' % (
#              format, re.escape(enum.formatinfo[format].prefix),
#              pats['enum'], re.escape(enum.formatinfo[format].suffix))

    patterns = {
          'title': r'h[0-6]\.( +|$)',
          #'explicit_markup': r'\.\.( +|$)',
          'line': r'(%(nonalphanum7bit)s)\1* *$' % pats,
          'text': r''}
    initial_transitions = (
            'title',
          #'explicit_markup',
          'text',
          'line',
      )

    def title(self, match, context, next_state):
        level = int(match.string[1])-1
        title = match.string[match.end():].lstrip()
        lineno = self.state_machine.abs_line_number()
        messages = []
        self.section(level, title, lineno-1, messages)
        self.parent += messages
        return [], next_state, []

    def section(self, level, title, lineno, messages):
        if self.check_subsection(level, title, lineno):
            self.new_subsection(level, title, lineno, messages)

    def check_subsection(self, level, title, lineno):

        memo = self.memo
        mylevel = memo.section_level

        source = "h%i. %s" % (level+1, title)

        if level == 0 and mylevel == 0:
        	return 1 # first section

        if level <= mylevel:            # sibling or supersection
            memo.section_level = level   # bubble up to parent section
            raise EOFError              # let parent section re-evaluate

        if level == mylevel + 1:        # immediate subsection
            return 1
        else:                           # invalid subsection
            self.parent += self.title_inconsistent(source, lineno)
            return None

    def title_inconsistent(self, sourcetext, lineno):
        src, srcline = self.state_machine.get_source_and_line(lineno)
        error = self.reporter.severe(
            'Title level inconsistent, %s while source is:' %
            (self.memo.section_level+1),
            nodes.literal_block('', sourcetext),
            source=src, line=srcline)
        return error

    def new_subsection(self, level, title, lineno, messages):
        """Append new subsection to document tree. On return, check level."""
        memo = self.memo
        mylevel = memo.section_level
        memo.section_level += 1
        section_node = nodes.section()
        self.parent += section_node
        textnodes, title_messages = self.inline_text(title, lineno)
        titlenode = nodes.title(title, '', *textnodes)
        name = normalize_name(titlenode.astext())
        section_node['names'].append(name)
        section_node += titlenode
        section_node += messages
        section_node += title_messages
        self.document.note_implicit_target(section_node, section_node)
        offset = self.state_machine.line_offset + 1
        absoffset = self.state_machine.abs_line_offset() + 1
        newabsoffset = self.nested_parse(
              self.state_machine.input_lines[offset:], input_offset=absoffset,
              node=section_node, match_titles=1)
        self.goto_line(newabsoffset)
        if memo.section_level <= mylevel: # can't handle next section?
            raise EOFError              # bubble up to supersection
        # reset section_level; next pass will detect it properly
        memo.section_level = mylevel

    def explicit_markup(self, match, context, next_state):
        """Footnotes, hyperlink targets, directives, comments."""
        nodelist, blank_finish = self.explicit_construct(match)
        self.parent += nodelist
        self.explicit_list(blank_finish)
        return [], next_state, []

    def line(self, match, context, next_state):
        """Section title overline or transition marker."""
        if self.state_machine.match_titles:
            return [match.string], 'Line', []
        elif match.string.strip() == '::':
            raise statemachine.TransitionCorrection('text')
        elif len(match.string.strip()) < 4:
            msg = self.reporter.info(
                'Unexpected possible title overline or transition.\n'
                "Treating it as ordinary text because it's so short.",
                line=self.state_machine.abs_line_number())
            self.parent += msg
            raise statemachine.TransitionCorrection('text')
        else:
            blocktext = self.state_machine.line
            msg = self.reporter.severe(
                  'Unexpected section title or transition.',
                  nodes.literal_block(blocktext, blocktext),
                  line=self.state_machine.abs_line_number())
            self.parent += msg
            return [], next_state, []

    def text(self, match, context, next_state):
        """Titles, definition lists, paragraphs."""
        #print 'body text', match, context, next_state
        return [match.string], 'Text', []


class Title(SimpleParserState):

    pass


class Text(SimpleParserState):

    patterns = {
                'text': r''
        }
    initial_transitions = [
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


state_classes = (Body, Title, Text)
