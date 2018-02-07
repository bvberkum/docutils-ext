"""
:Created: 2018-02-03

TODO: Record sections, and nested lists (including field-list's and definition-
list's) to file

Format requirements
- '/'-separated path of title/term/field/index; the 'topic' path.
  maybe '*' and '-' or [] for anon list.
- maybe path param with line number, block line count ie dsp/wid in trms of lines
  as attribute for output record
- optionally record (empty) comment as sentinel to close 'topic' path. mark
  as final; it as closed for further editorial or automatic updates.
  XXX: do stuff if sentinel has arguments/contents

Usage with .mpe Reader::

    $ python tools/rst2pprint \
            --record-outline=/tmp/doc.outline \
            document.rst /dev/null

"""
from __future__ import print_function

import sys

from docutils import transforms, nodes
import nabu.extract
from nabu.extract import ExtractorStorage
from dotmpe.du import util


#class RecordOutline(nabu.extract.Extractor): XXX: spec is different
class RecordOutline(transforms.Transform):

    """
    Extract outline from document and write to file.

    The file can be provided to apply, to use the extractor in customized
    settings other than part of a docutils.Reader instance.

    The outline consists of nested items of single or several types,
    according to schema provided at outline-schema. Normally the schema is
    of a dictionary kind, with no lists. Each record has a key, with
    accompanying label, and a value if found.

    XXX: disable values, output path only

    XXX: vary todo.txt-style attributes and URL-path params.

    XXX: or process values, separate attributes, selectively output

    XXX: mix with sentinel scan, possibly order based on v-streams

    XXX: enabling lists in outlines, disable/rewrite at points? hmm..

    XXX: set other types for value: date, URL, path, attributes.. metadata, can
    get too complicated to be practical

    """

    settings_spec = (
        (
            'Record extracted outlines, each item to a line',
            ['--record-outline'],
            {'default':None, 'metavar':'FILE' }
        ), (
            'The nodes to extract as terms, and find an according value for',
            ['--outline-schema-terms'],
            {'default': [
                'title',
                'term',
                'field_name'
              ], 'metavar':'TYPE' }
        ), (
            'Append recorded outlines at end of file iso. truncating existing file',
            ['--append-outline-records'],
            {'default':False, 'action':'store_true' }
        ), (
            'Format for outlines file: path, or json. ',
            ['--record-outline-format'],
            {'default':'path', 'metavar':'NAME' }
        ), (
            'Dont run outline extractor, even if file/dbref is given. ',
            ['--no-outline-record'], { 'dest': 'record_outline', 'action': 'store_false' }
        ),
    )

    default_priority = 880

    def apply(self, f=None, unid=None, storage=None, **kwargs):
        doc = self.document
        g = doc.settings

        if not getattr(g, 'record_outline', None):
            return

        v = OutlineVisitor(doc, g.outline_schema_terms)
        doc.walk(v)
        self.outline = v.terms

        self.write_outline(f)

    def write_outline(self, f=None):
        g = self.document.settings

        if f:
            self.f = f
        else:
            mode = g.append_outline_records and 'a+' or 'w+'
            self.f = open(g.record_outline, mode)

        format = getattr(self, 'format_%s' % g.record_outline_format)
        self.f.write(format(self.outline, g))
        self.f.close()

    def format_json(self, outline, g):
        import json
        return json.dumps([
                util.node_idspath(n) for n in outline
            ])

    def format_path(self, outline, g):
        return "\n".join([
                "/".join(util.node_idspath(n, g)) for n in outline
            ])

        """TODO: table output format with some fields
    def format_tab(self, outline, g):
            print(srcname, s.line,
        for outline_node in outline:
            l = outline_format[g.record_outline_format](outline_node, g)
        srcname = doc.settings._source
        print('--------------')
        for n in v.terms:
            s = n
            while not s.line:
                print(s)
                s = s.parent
            #print(srcname, s.line, "/".join(util.node_idspath(n, g)))
        """


class OutlineVisitor(nodes.NodeVisitor):

    """
    Simplified Outline visitor. Iso. tracking context (state, paths), add
    attributes.

    Add node-for attribute to container for every term-type node found.

    This assumes term-type nodes are exactly one level below their container.

    NOTE: looked at lines, but need some other work to get at proper ranges,
    see range transform
    """

    def __init__(self, doc, term_type):
        nodes.NodeVisitor.__init__(self, doc)
        self.term_type = term_type
        self.terms = []

    def unknown_visit(self, node):
        self._mark_outline_node(node)

    def unknown_departure(self, node): pass

    def _mark_outline_node(self, node):
        nt = node.__class__.__name__
        if nt in self.term_type:
            node_id = nodes.make_id(node.astext())
            assert 'ids' in node.attributes, 'TOTEST'
            if node_id not in node.attributes['ids']:
                node.attributes['ids'].append(node_id)
            self.terms.append(node)
            node['outline-label'] = True
            node.parent['node-for'] = node_id
