"""docutils HTML4CSS1 writer with support for extensions in this package.

Copyleft 2009  Berend van Berkum <dev@dotmpe.com>
This file has been placed in the Public Domain.
"""
import os
from docutils import utils, nodes, frontend, io
from docutils.writers import html4css1


MIME_HTML = 'text/html'


def get_script_list(settings):
    """
    Retrieve list of script references from the settings object.
    """
    if settings.script_path:
        assert not settings.script, (
               'script and script_path are mutually exclusive.')
        return settings.script_path.split(",")
    elif settings.script:
        return settings.script.split(",")
    else:
        return []

class HTMLTranslator(html4css1.HTMLTranslator):
    """
    This overrides some things on the html4css1 translator,
    and adds visitors for:

    - include
    - left/right margin

    Also adds functionality for lists of embedded or linked scripts.
    """

    script_link = '<script src="%s" type="text/javascript"></script>\n'
    embedded_script = '<script type="text/css">\n\n%s\n</script>\n'

    def __init__(self, document):
        html4css1.HTMLTranslator.__init__(self, document)
        self.left_margin = []
        self.right_margin = []
       
        settings = document.settings
        scripts = get_script_list(settings)
        if settings.script_path and not(settings.embed_script):
            scripts = [utils.relative_path(settings._destination, script)
                      for script in scripts]
        if settings.embed_script:
            # XXX: not tested
            settings.record_dependencies.add(*scripts)
            self.script = [self.embedded_script %
                io.FileInput(source_path=script, encoding='utf-8').read()
                for script in scripts]
        else: # link to scripts
            self.script = [self.script_link % self.encode(script)
                               for script in scripts]

    # New visitors
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

    # Overrides utils
    def starttag(self, node, tagname, suffix='\n', empty=0, **attributes):
        # XXX: dont allow frame(=void) or rules(=none)
        if 'rules' in attributes:
            del attributes['rules'] 
        if 'frame' in attributes:
            del attributes['frame'] 
        return html4css1.HTMLTranslator.starttag(self, node, tagname, suffix=suffix,
                empty=empty, **attributes)

    # Override visitor
    # FIXME: should only allow in output for certain clients
    def visit_include(self, node):
        href = node['refuri']
        # TODO: mediatype
        obj=self.starttag(node, 'object', data=href, TYPE=MIME_HTML, CLASS='docutils include')
        self.body.append(obj)
        self.body.append(self.starttag(node, 'div', CLASS='unsupported'))
        self.body.append('Warning: remote content missing (%s)</div>' % href)
        self.body.append('</object>')

    def depart_include(self, node):
        pass

    def visit_system_message(self, node):
        """
        Override: 
        - ext. CLASS attr for DIV
        """
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

    settings_spec = html4css1.Writer.settings_spec + (
        'dotmpe html4css1 extensions',
        None,
        (('Specify comma separated list of JavaScript URLs. ',
          ['--script'],
          { 'metavar': '<URL>' }),
         ('Specify comma separated list of JavaScript URLs. ',
          ['--script-path'],
          { 'metavar': '<file>', 'overrides': 'script' }),
         ('Embed the script(s) in the output HTML file.  The script '
          'files must be accessible during processing. This is the default.',
          ['--embed-script'],
          {'default': 1, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Link to the script(s) in the output HTML file. '
          'Default: embed scripts.',
          ['--link-script'],
          {'dest': 'embed_script', 'action': 'store_false'}),
      ))

    default_template = 'html-template.txt'

    default_template_path = utils.relative_path(
        os.path.join(os.getcwd(), 'dummy'),
        os.path.join(os.path.dirname(__file__), default_template))

    settings_default_overrides = {
        'template': default_template_path,#'html-template.txt',
    }

    relative_path_settings = html4css1.Writer.relative_path_settings + ('script_path',)

    visitor_attributes = \
        html4css1.Writer.visitor_attributes + \
        ( 'left_margin', 'right_margin', 'script', )

    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = HTMLTranslator


