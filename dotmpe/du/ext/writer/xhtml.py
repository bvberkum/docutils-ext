# $Id$

"""
Plain XHTML for easy adapting into ones own (template) specific site/web-app..?

TODO: everything.. but first lots todo at Blue Lines.
TODO: validate (tidy).
"""

from docutils import writers, nodes, frontend  
from docutils.writers import html4css1 as html
from docutils.transforms import writer_aux


class Writer(writers.Writer):

    example_default_settings_spec = ( # XXX: nicked from html4css1,
            # for what opts are supported
        'XHTML-Specific Options',
        None,
        (('Specify the template file (UTF-8 encoded).  Default is "%s".'
          % html.Writer.default_template_path,
          ['--template'],
          {'default': html.Writer.default_template_path, 'metavar': '<file>'}),
        ('Specify comma separated list of stylesheet URLs. '
          'Overrides previous --stylesheet and --stylesheet-path settings.',
          ['--stylesheet'],
          {'metavar': '<URL>', 'overrides': 'stylesheet_path'}),
         ('Specify comma separated list of stylesheet paths. '
          'With --link-stylesheet, '
          'the path is rewritten relative to the output HTML file. '
          'Default: "%s"', # FIXME % html.Writer.default_stylesheet_path,
          ['--stylesheet-path'],
          {'metavar': '<file>', 'overrides': 'stylesheet',
           'default': "",}),#html.Writer.default_stylesheet_path}),
         ('Embed the stylesheet(s) in the output HTML file.  The stylesheet '
          'files must be accessible during processing. This is the default.',
          ['--embed-stylesheet'],
          {'default': 1, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Link to the stylesheet(s) in the output HTML file. '
          'Default: embed stylesheets.',
          ['--link-stylesheet'],
          {'dest': 'embed_stylesheet', 'action': 'store_false'}),
         ('Specify the initial header level.  Default is 1 for "<h1>".  '
          'Does not affect document title & subtitle (see --no-doc-title).',
          ['--initial-header-level'],
          {'choices': '1 2 3 4 5 6'.split(), 'default': '1',
           'metavar': '<level>'}),
         ('Specify the maximum width (in characters) for one-column field '
          'names.  Longer field names will span an entire row of the table '
          'used to render the field list.  Default is 14 characters.  '
          'Use 0 for "no limit".',
          ['--field-name-limit'],
          {'default': 14, 'metavar': '<level>',
           'validator': frontend.validate_nonnegative_int}),
         ('Specify the maximum width (in characters) for options in option '
          'lists.  Longer options will span an entire row of the table used '
          'to render the option list.  Default is 14 characters.  '
          'Use 0 for "no limit".',
          ['--option-limit'],
          {'default': 14, 'metavar': '<level>',
           'validator': frontend.validate_nonnegative_int}),
         ('Format for footnote references: one of "superscript" or '
          '"brackets".  Default is "brackets".',
          ['--footnote-references'],
          {'choices': ['superscript', 'brackets'], 'default': 'brackets',
           'metavar': '<format>',
           'overrides': 'trim_footnote_reference_space'}),
         ('Format for block quote attributions: one of "dash" (em-dash '
          'prefix), "parentheses"/"parens", or "none".  Default is "dash".',
          ['--attribution'],
          {'choices': ['dash', 'parentheses', 'parens', 'none'],
           'default': 'dash', 'metavar': '<format>'}),
         ('Remove extra vertical whitespace between items of "simple" bullet '
          'lists and enumerated lists.  Default: enabled.',
          ['--compact-lists'],
          {'default': 1, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Disable compact simple bullet and enumerated lists.',
          ['--no-compact-lists'],
          {'dest': 'compact_lists', 'action': 'store_false'}),
         ('Remove extra vertical whitespace between items of simple field '
          'lists.  Default: enabled.',
          ['--compact-field-lists'],
          {'default': 1, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Disable compact simple field lists.',
          ['--no-compact-field-lists'],
          {'dest': 'compact_field_lists', 'action': 'store_false'}),
         ('Added to standard table classes. '
          'Defined styles: "borderless". Default: ""',
          ['--table-style'],
          {'default': ''}),
         ('Omit the XML declaration.  Use with caution.',
          ['--no-xml-declaration'],
          {'dest': 'xml_declaration', 'default': 1, 'action': 'store_false',
           'validator': frontend.validate_boolean}),
         ('Obfuscate email addresses to confuse harvesters while still '
          'keeping email links usable with standards-compliant browsers.',
          ['--cloak-email-addresses'],
          {'action': 'store_true', 'validator': frontend.validate_boolean}),))

    def get_transforms(self):
        return writers.Writer.get_transforms(self) + [
            writer_aux.Admonitions
                ]

    def __init__(self):
        writers.Writer.__init__(self)

    def translate(self):
        """
        Do final translation of `self.document` into `self.output`.  Called
        from `write`. All standard elements (listed in
        `docutils.nodes.node_class_names`) and possibly non-standard elements
        used by the current Reader must be supported.

        The method of document translation here is not of the Visitor pattern Du
        usually deploys but a top-down flatten of the tree, each node-type is
        translated in-place. 

        XXX: Does this remove some flexibility in constructing the output
        document? ie. node content/attributes have not influence on other
        elements...
        It feels more appropiate though. Writer transforms should have prepared the
        document for the particular output format.
        """

    def assemble_parts(self):
        """Assemble the `self.parts` dictionary.  Extend in subclasses."""
        #self.parts['whole'] = self.output
        #self.parts['encoding'] = self.document.settings.output_encoding
        #self.parts['version'] = docutils.__version__


def flatten_document(node):
    # meta = [ct % settings.output_encoding, 
    # self.generator % docutils.__version__ ]
    # head_prefix = [xml_decl % settings.output_encoding]
    # html_prolog = [xml_decl, doctype]
    # head = meta[:]
    # head.append(node.get('title',''))
    # other head tag 
    # parts.update{
    # 'fragment': flatten(node)
    # 'html_body': <body..>%(pre_doc_info)%(docinfo)flatten(node)</body>
    
    # 
    pass


