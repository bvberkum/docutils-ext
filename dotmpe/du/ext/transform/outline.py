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

from docutils import transforms, nodes
import nabu.extract
from nabu.extract import ExtractorStorage
from dotmpe.du import util


#class RecordOutline(nabu.extract.Extractor): spec is different
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
        #'Outline transform options',
        #None,
        #((
        #     'Database to store outline. ',
        #     ['--outline-database'],
        #     {
        #         'metavar':'PATH',
        #         'validator': util.optparse_init_anydbm,
        #     }
        #),(
        (
            'Record extracted outlines, each item to a line',
            ['--record-outline'],
            {'default':None, 'metavar':'FILE' }
        ), (
            'TODO: Define outline schema. The default is to generate one, from '
            +'instances found for outline-schema-terms, and the first paragarph '
            +'or the text content of paired values node-type instance, found '
            +'after the term in the same container',
            ['--outline-schema'],
            {'default':None, 'metavar':'FILE' }
        ), (
            'The nodes to extract as terms, and find an according value for',
            ['--outline-schema-terms'],
            {'default': ['title', 'term', 'field_name'], 'metavar':'TYPE' }
        ), (
            'The value types to extract',
            ['--outline-schema-values'],
            {'default': ['paragraph', 'definition/paragraph', 'field_body/paragraph'], 'metavar':'TYPE' }
        ), (
            'Append recorded outlines at end of file iso. truncating existing file',
            ['--append-outline-records'],
            {'default':False, 'action':'store_true' }
        ), (
            'Format for outlines file: path, text or todo.txt. ',
            ['--record-outline-format'],
            {'default': 'url', 'metavar':'NAME' }
        ), (
            'Dont run outline extractor, even if file/dbref is given. ',
            ['--no-outline-record'], { 'dest': 'record_outline', 'action': 'store_false' }
        ),#)
    )

    default_priority = 880

    def apply(self, f=None, unid=None, storage=None, **kwargs):
        g = self.document.settings
        #if g.dbref and ( g.no_db or g.no_outline):
        if not getattr(g, 'record_outline', None):
            return

        if f:
            self.f = f
        else:
            mode = g.append_outline_records and 'a+' or 'w+'
            self.f = open(g.record_outline, mode)


        if g.outline_schema:
            assert not g.outline_schema, 'TODO'

        else:
            #value_ntypes = [ getattr(nodes, nt) for nt in g.outline_schema_values ]

            #term_ntypes = [ getattr(nodes, nt) for nt in g.outline_schema_terms ]
            for i, nt in enumerate(g.outline_schema_terms):
                for term in self.document.traverse(getattr(nodes, nt)):
                    print(term, file=sys.stderr)
                    #print(term.parent, file=sys.stderr)
                    #values = term.parent.traverse( nt[i] ):

        #v = OutlineVisitor(self.document, storage)
        #self.document.walk(v)


import sys

class OutlineVisitor(nodes.SparseNodeVisitor):

    def __init__(self, doc, store):
        nodes.SparseNodeVisitor.__init__(self, doc)
        self.store = store
        self.stack = []
        self.sections = {}
        srcname = doc.settings._source
        print(srcname, file=sys.stderr)

    def push_stack(self, node):
        supersection = None
        if self.stack:
            supersection = self.stack[-1]
        self.stack.append(node)
    def path(self):
        return ".".join( [ n.astext() for n in self.stack ] )

    def visit_term(self, node):
        self.push_stack(node)
        print(self.path(), file=sys.stderr)
    def depart_term(self, node):
        assert self.stack.pop() == node

    def visit_section(self, node):
        self.push_stack(node)
    def depart_section(self, node):
        assert self.stack.pop() == node

