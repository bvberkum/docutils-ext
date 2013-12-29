"""
.mpe htdocs extractor
"""
from datetime import datetime 

from nabu import extract
from docutils import nodes
#from dotmpe.du.ext import extractor
from script_mpe import htdocs, taxus
from script_mpe.taxus.util import get_session



class HtdocsExtractor(extract.Extractor):

    """
    See dotmpe.du.form for documentation.
    """

    settings_spec = (
        'HtDocs Extractor Options',
        None,
        [(
             'todo',
             ['--todo'],
             {
                 'metavar':'PATH', 
#                 'validator': util.optparse_init_anydbm,
             }
        ),] 
    )

    default_priority = 500

    # See dotmpe.du.form for settings_spec

    def init_parser(cls):
        " do some env. massaging if needed. "

    fields_spec = []

    def apply(self, unid=None, storage=None, **kwds):
        # - get (new) ref for each definition term
        # - accumulated definition descriptions:
        #   append lists to some log,
        #   
        # XXX print unid, storage, kwds
        # create visitor for doc, add storage for lookup and possible updates to existing items
        # xxx: must rewrite document for updates, but rst2rst is not happening yet
        v = TinkerVisitor(self.document, storage)
        self.document.walk(v)
        v.finalize()


class HtdocsStorage(extract.ExtractorStorage):

    def __init__(self, dbref='sqlite', initdb=False):
        print 'HtdocsStorage', 'init', dbref, initdb
        self.sa = get_session(dbref, initdb)

    def store(self, source_id, *args):
        print 'store', source_id, args
        this.sa.query(source_id)

    def clear(self, source_id):

        pass

    def reset_schema(self, source_id):
        raise NotImplemented


class TinkerVisitor(nodes.SparseNodeVisitor):

    def __init__(self, doc, store):
        nodes.SparseNodeVisitor.__init__(self, doc)
        self.store = store

    def finalize(self):
        pass

#    def visit_definition_list(self, node):
#        print 'visit_definition_list', node

#    def visit_definition_list_item(self, node):
#        print 'visit_definition_list_item', node

    def visit_term(self, node):

        sa = self.store.sa
        def now():
            return datetime.now()

        print 'visit_term', node.astext()
        terms = node.astext().split()
        for i, term in enumerate(terms):
            matches = self.store.sa.query(taxus.semweb.Description)\
                    .filter(taxus.semweb.Description.name==term).all()
            if not matches:
                description = taxus.Description(
                        name=term, date_added=now())
                sa.add(description)
                sa.commit()
                print 'new', description.name

        # XXX it is not the intention to do a string lookup, each node should
        # carry semantics so there may be term_1 term_2 to denote different terms
        # Currently this means the writer should be explicit
        # Another routine is needed (in taxus) to clean up unreferenced nodes

    def visit_definition(self, node):
        print 'visit_description'#, node.astext()

    def depart_definition(self, node):
        print 'depart_definition'#, node.astext()

    def visit_list_item(self, node):
        print 'visit_list_item', node


Extractor = HtdocsExtractor
Storage = HtdocsStorage

