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
        v.unid = unid
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
             file_name TEXT NOT NULL DEFAULT "<source>",
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

    def __init__(self, session=None, dbref=None):
        if not session:
            assert dbref, ("Missing SQL-alchemy DB ref", self)
            # set for SA, then get engine to use as DBAPI-2.0 compatible connection
            self.session = get_session(dbref, True)
        else:
            self.session = session
        # XXX can I get raw-connection from self.session?
        #self.connection = SqlBase.metadata.bind.raw_connection()
        #logger.info("Connected to %s", self.connection)
        logger.info("Extractor store to %s", self.session)

        class Title(SqlBase):
            __table__ = SqlBase.metadata.tables['titles']
        self.Title = Title

    def store(self, source_id, *args):
        pass

    def clear(self, source_id):
        pass

    # custom

    def find_term(self, visitor, node):

        s = self.session
        q = s.query(self.Title)

        def now():
            return datetime.now()

        terms = node.astext().split()
        for i, t in enumerate(terms):
            if t.isalnum():
                q = q.filter(self.Title.value.like("%%%s%%" % t))
        candidates = q.all()

        print terms
        for c in candidates:
            print c.unid, c.value, c.file_name

        #assert not candidates, (candidates, term)

        # TODO get line number
        term = node.astext()
        t = self.Title(value=term, file_name=visitor.unid)
        s.add(t)
        s.commit()



class TinkerVisitor(nodes.SparseNodeVisitor):

    def __init__(self, doc, store):
        nodes.SparseNodeVisitor.__init__(self, doc)
        self.store = store

    def finalize(self):
        pass # XXX

    def visit_term(self, node):

        s = self.store

        s.find_term(self, node)

        # XXX it is not the intention to do a string lookup, each node should
        # carry semantics so there may be term_1 term_2 to denote different terms
        # Currently this means the writer should be explicit
        # Another routine is needed (in taxus) to clean up unreferenced nodes



Extractor = HtdocsExtractor
Storage = HtdocsStorage

