"""
Embedded Atlassian Confluence support for standard Docutils.

* Parser for Confluence reads Confluence into raw node with 
  'confluence-embedded' format.

TODO
    - Support limited interpreted confluence in literal blocks?
    - Embed raw rST in confluence markup?
"""

import docutils
from docutils import frontend, parsers



class Parser(parsers.Parser):

    """
    Embedded Atlassian Confluence markup parser.
    This imports raw confluence as `raw` Du document nodes.
    """

    supported = ( 'confluence-embedded', )
    """Aliases this parser supports."""

    settings_spec = (
        'Embedded Atlassian Confluence Parser Options',
        "This embeds raw confluence markup in `raw` nodes, "
        "it does not interpret any confluence markup. ",
        (
         ('Set number of spaces for tab expansion (default 8).',
          ['--tab-width'],
          {'metavar': '<width>', 'type': 'int', 'default': 8,
           'validator': frontend.validate_nonnegative_int}),
          ))

    config_section = 'atlassian parser'
    config_section_dependencies = ('parsers',)

    def __init__(self):
        pass

    def parse(self, inputstring, document):
        """Parse `inputstring` and populate `document`, a document tree."""

        # XXX: cannot parametrize parse based on specific alias, only through
        # additional command-line options. Set reader_name or input_format on
        # settings?
        #print "input_format="+document.settings...?
        #if input_format == 'confluence-embedded'
        attributes = {'format': 'confluence'}
        embedded_acw = docutils.nodes.raw('', inputstring, **attributes)

        document += [embedded_acw]


