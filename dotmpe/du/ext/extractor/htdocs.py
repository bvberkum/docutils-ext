"""
.mpe htdocs extractor

Inline (title, literal, reference)
    ..
Definition Terms
    - The blocks or list/items under the term may be appended somehow to a
      resource matching term.

"""
from datetime import datetime 
from pprint import pformat

import json

from sqlalchemy import Table

from docutils import nodes
from dotmpe.du import util
from dotmpe.du.ext import extractor

from script_mpe import taxus
from script_mpe.taxus.init import SqlBase
from script_mpe.taxus.util import get_session



logger = util.get_log(__name__)

class HtdocsExtractor(extractor.Extractor):

    """
    TODO: store titles in rel. DB.

    Record:
        - value (unicode string)
        - xml-path (used to infer type?)
        - file
        - char_offset (if I can get it from the parser)
        - line_offset

    Some global identifiers could be inferred. Make up some schemes.. titles,
    definition terms, roles.
    Global could mean include <doc-id>. Var. URIRef options here.
    """

    default_priority = 500

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
        print pformat(v.terms)
        print self.document.messages


class HtdocsStorage(extractor.SQLiteExtractorStorage):

    """
    Work in progress: SQLAlchemy storage?
    """

    sql_relations_unid = [
        ('titles', 'TABLE',
         """

          CREATE TABLE titles
          (
             unid INTEGER PRIMARY KEY AUTOINCREMENT,
             sid TEXT,
             value TEXT NOT NULL,
             file TEXT NOT NULL DEFAULT "<source>",
             char_offset INTEGER,
             line_offset INTEGER,
             url TEXT
          );

        """),
    ]

    sql_relations = [
#        ('title_value_idx', 'INDEX', """
#
#          CREATE INDEX title_value_idx ON titles (value);
#
#         """)
    ]

    def __init__(self, engine=None, dbref=None):
        if not engine:
            assert dbref, ("Missing SQL-alchemy DB ref", self)
            # set for SA, get engine to use as DBAPI-2.0 compatible connection
            self.session = get_session(dbref, True)
            self.connection = SqlBase.metadata.bind.raw_connection()

        else:
            self.connection = engine

        logger.info("Connected to %s", self.connection)

    # Extractor
    def store(self, source_id, *args):
        """
        TODO main store api, node-subclass of document?
        """
        print 'store', source_id, args
        this.sa.query(source_id)

    def clear(self, source_id):
        pass

    # custom
    def find_term(self, term):
        engine = SqlBase.metadata.bind
        t = Table('titles', SqlBase.metadata, autoload=True,
                autoload_with=engine)
        return
        def now():
            return datetime.now()


        terms = term.split()
        for i, term in enumerate(terms):
            # TODO: query term 
            print i, term
            continue

            matches = session.query(taxus.semweb.Description)\
                    .filter(taxus.semweb.Description.name==term).all()
            if not matches:
                description = taxus.Description(
                        name=term, date_added=now())
                session.add(description)
                session.commit()
                print 'new', description.name

    # 
#    def retrieve_

def now():
    return datetime.now()

class TinkerVisitor(nodes.SparseNodeVisitor):

    """
    Visit term nodes, interpret one or more references, and update.
    """

    def __init__(self, doc, store):
        nodes.SparseNodeVisitor.__init__(self, doc)
        self.store = store
        self.stack = []
        self.terms = {}

    def finalize(self):
        pass

#    def visit_definition_list(self, node):
#        pass#print 'visit_definition_list', node
#        return True
#    def visit_definition_list_item(self, node):
#        print 'visit_definition_list_item', node

    def push_stack(self, node):
        superterm = None
        if self.stack:
            superterm = self.stack[-1]
        self.stack.append(node)

    def visit_term(self, node):
        self.push_stack(node)
        t = node.astext()
        if t not in self.terms:
            self.terms[t] = {}
#        self.current = self.terms[t]
        print 'visit_term', t
        return

        for i, term in enumerate(terms):
            print i, term
            continue

            sa = self.store.sa
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
    def depart_term(self, node):
        assert self.stack.pop() == node

#    def visit_definition(self, node):
#        print 'visit_description'#, node.astext()
#
#    def depart_definition(self, node):
#        pass#print 'depart_definition'#, node.astext()
#        #return True
#
#    def visit_list_item(self, node):
#        pass#print 'visit_list_item', node


Extractor = HtdocsExtractor
Storage = HtdocsStorage

