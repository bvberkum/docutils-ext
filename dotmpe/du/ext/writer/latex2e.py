"""
"""
from docutils.writers import latex2e
from docutils.writers.latex2e import PreambleCmds


class Writer(latex2e.Writer):

    def __init__(self):
        latex2e.Writer.__init__(self)
        self.translator_class = LaTeXTranslator


import dotmpe.du.ext.parser.rst.directive.images

class LaTeXTranslator(latex2e.LaTeXTranslator):

    def depart_figure(self, node):
        if 'label' in node and node['label']:
            self.out.append('\\label{fig:%s}\n' % node['label'])
        self.out.append('\\end{figure}\n')

    def visit_footnote(self, node):
        try:
            backref = node['backrefs'][0]
        except IndexError:
            backref = node['ids'][0] # no backref, use self-ref instead
        if self.settings.figure_footnotes:
            self.requirements['~fnt_floats'] = PreambleCmds.footnote_floats
            self.out.append('\\begin{figure}[b]')
            self.append_hypertargets(node)
            if node.get('id') == node.get('name'):  # explicite label
                self.out += self.ids_to_labels(node)
        elif self.docutils_footnotes:
            self.fallbacks['footnotes'] = PreambleCmds.footnotes
            num,text = node.astext().split(None,1)
            if self.settings.footnote_references == 'brackets':
                num = '[%s]' % num
            self.out.append('%%\n\\DUfootnotetext{%s}{%s}{%s}{' %
                            (node['ids'][0], backref, self.encode(num)))
            if node['ids'] == node['names']:
                self.out += self.ids_to_labels(node)
            # mask newline to prevent spurious whitespace:
            self.out.append('%')
        ## else:  # TODO: "real" LaTeX \footnote{}s

    def visit_figure_ref(self, node):
        """figure reference role"""
        if node['classes']:
            self.visit_inline(node)
        self.body.append('\\ref{fig:%s}' % node['target'])
        raise nodes.SkipNode

    def depart_figure_ref(self, node):
        if node['classes']:
            self.depart_inline(node)


