"""
:Created: 2018-02-07

Usage with .mpe Reader::

    $ python tools/rst2pprint \
            --record-outline=/tmp/doc.outline \
            document.rst /dev/null

"""
from __future__ import print_function

from docutils import transforms, nodes
from dotmpe.du import util


class RecordRanges(transforms.Transform):

    settings_spec = (
        (
            'Record ranges',
            ['--record-ranges'],
            {'default':None, 'metavar':'FILE' }
        ), (
            'Record ranges',
            ['--record-range-nodes'],
            {'default':None, 'metavar':'NAME' }
        ),
    )

    default_priority = 880

    def apply(self, f=None, unid=None, storage=None, **kwargs):
        doc = self.document
        g = doc.settings

        if not getattr(g, 'record_ranges', None):
            return

        v = DspVisitor(doc, g.record_range_nodes)
        doc.walk(v)


class DspVisitor(nodes.NodeVisitor):

    def __init__(self, doc, term_type):
        nodes.NodeVisitor.__init__(self, doc)
        self.term_type = term_type

    def unknown_visit(self, node):
        self._mark_dsp(node)

    def _mark_dsp(self, node):
        if isinstance(node, nodes.Node) and node.line:
            #print(node.line, util.node_nodepath(node))
            if isinstance(node, nodes.Element):
                node.attributes['line'] = node.line
        else:
            pass #print('-', util.node_nodepath(node))

