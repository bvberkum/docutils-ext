from docutils import nodes
import nabu.extract
from nabu.extract import ExtractorStorage
from dotmpe.du import util


class Extractor(nabu.extract.Extractor):

    settings_spec = (
        'Reference Extractor Options',
        None,
        ((
             'Database to store references. ',
             ['--reference-database'],
             {
                 'metavar':'PATH',
                 'validator': util.optparse_init_anydbm,
             }
        ),)
    )

    default_priority = 900

    def apply(self, unid=None, storage=None, **kwargs):
        v = SectionVisitor(self.document, storage)
        self.document.walk(v)


class Storage(ExtractorStorage):
    def __init__(self):
        pass


class SectionVisitor(nodes.SparseNodeVisitor):
    def __init__(self, doc, store):
        nodes.SparseNodeVisitor.__init__(self, doc)
        self.store = store
        self.stack = []
        self.sections = {}
        srcname = doc.settings._source
        print srcname

    def push_stack(self, node):
        supersection = None
        if self.stack:
            supersection = self.stack[-1]
        self.stack.append(node)
    def path(self):
        return ".".join( [ n.astext() for n in self.stack ] )

    def visit_term(self, node):
        self.push_stack(node)
        print self.path()
    def depart_term(self, node):
        assert self.stack.pop() == node

    def visit_section(self, node):
        self.push_stack(node)
    def depart_section(self, node):
        assert self.stack.pop() == node


