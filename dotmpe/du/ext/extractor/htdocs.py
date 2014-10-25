"""
.mpe htdocs extractor

dev phase
1. Uniquely identify each section, term or reference in a document.
2. Interactively identify above nodes; need rSt document in-place rewrite.

Phase I
-------
- Work in progress extacting terms. 
  Eventually many types of nodes could qualify.

  Simple anydbm based storage. db is shared between extractors.  

XXX can this be generic, or should build different one for note, journal, etc.
    gonna need lots of path- or context-specific handlers to determine global
    ID.
"""
from datetime import datetime 

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

    def store(self, source_id, *args):
        pass

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

        #def now():
        #    return datetime.now()

        #print 'visit_term', node.astext()
        #terms = node.astext().split()
        #for i, term in enumerate(terms):
        #    print i, term
        #    continue

        #    sa = self.store.sa
        #    matches = self.store.sa.query(taxus.semweb.Description)\
        #            .filter(taxus.semweb.Description.name==term).all()
        #    if not matches:
        #        description = taxus.Description(
        #                name=term, date_added=now())
        #        sa.add(description)
        #        sa.commit()
        #        print 'new', description.name

        s = self.store

        s.find_term(node.astext())

        # XXX it is not the intention to do a string lookup, each node should
        # carry semantics so there may be term_1 term_2 to denote different terms
        # Currently this means the writer should be explicit
        # Another routine is needed (in taxus) to clean up unreferenced nodes

    def visit_definition(self, node):
        pass#print 'visit_description'#, node.astext()

    def depart_definition(self, node):
        pass#print 'depart_definition'#, node.astext()

    def visit_list_item(self, node):
        pass#print 'visit_list_item', node


Extractor = HtdocsExtractor
Storage = HtdocsStorage

