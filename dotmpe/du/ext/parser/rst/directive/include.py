import os
from docutils import utils, nodes
from docutils.parsers.rst import directives, roles, states
from docutils.parsers.rst import Directive
#from docutils.parsers.rst.directives import misc
from dotmpe.du.ext.node.include import include


#class Include(misc.Include):
class Include(Directive):

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'literal': directives.flag,
                   'encoding': directives.encoding,
                   'tab-width': int,
                   'start-line': int,
                   'end-line': int,
                   'start-after': directives.unchanged_required,
                   'end-before': directives.unchanged_required}

    standard_include_path = os.path.join(os.path.dirname(states.__file__),
                                         'include')

    def run(self):
        """Include a reST file as part of the content of this reST file."""
        #if not self.state.document.settings.file_insertion_enabled:
        #    raise self.warning('"%s" directive disabled.' % self.name)
        source = self.state_machine.input_lines.source(
            self.lineno - self.state_machine.input_offset - 1)
        source_dir = os.path.dirname(os.path.abspath(source))
        path = directives.path(self.arguments[0])
        if path.startswith('<') and path.endswith('>'):
            path = os.path.join(self.standard_include_path, path[1:-1])
        path = os.path.normpath(os.path.join(source_dir, path))
        path = utils.relative_path(None, path)
        path = nodes.reprunicode(path)
        encoding = self.options.get(
            'encoding', self.state.document.settings.input_encoding)
        tab_width = self.options.get(
            'tab-width', self.state.document.settings.tab_width)
        startline = self.options.get('start-line', None)
        endline = self.options.get('end-line', None)
        after_text = self.options.get('start-after', None)
        before_text = self.options.get('end-before', None)
        self.state.document.settings.record_dependencies.add(path)
        return [include('', refuri=path, encoding=encoding, tab_width=tab_width, 
                startline=startline, endline=endline,
                start_after=after_text, end_before=before_text)]


