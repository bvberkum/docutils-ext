"""
TODO: .mpe htdocs extractor

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
from dotmpe.du.mpe_du_util import SqlBase, get_session
from dotmpe.du.ext import extractor




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

    # XXX: not used by Builder unless staticly hardcoded into its specs.
    settings_spec = (
        'Htdocs extractor',
        None,
        ((
             '',
             ['--no-proc'], { 'action': 'store_true' }
        ),)
    )

    default_priority = 500

    def init_parser(cls):
        " do some env. massaging if needed. "

    fields_spec = []

    def apply(self, unid=None, storage=None, **kwds):
        g = self.document.settings
        if g.no_proc:
            return
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
        self.session = session
        if not session:
            assert dbref, ("Missing SQL-alchemy DB ref", self)
            # set for SA, then get engine to use as DBAPI-2.0 compatible connection
            self.session = get_session(dbref, True)
        # XXX can I get raw-connection from self.session?
        #self.connection = SqlBase.metadata.bind.raw_connection()
        #logger.info("Connected to %s", self.connection)
        logger.info("Extractor store to %s", self.session)

        class Title(SqlBase):
            __table__ = SqlBase.metadata.tables['titles']
        self.Title = Title

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

    def find_term(self, visitor, node):

        s = self.session
        q = s.query(self.Title)

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

    #
#    def retrieve_


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
        pass # XXX

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
                        name=term, date_added=datetime.now())
                sa.add(description)
                sa.commit()
                print 'new', description.name
        s.find_term(self, node)

        # XXX it is not the intention to do a string lookup, each node should
        # carry semantics so there may be term_1 term_2 to denote different terms
        # Currently this means the writer should be explicit
        # Another routine is needed (in taxus) to clean up unreferenced nodes
    def depart_term(self, node):
        assert self.stack.pop() == node



Extractor = HtdocsExtractor
Storage = HtdocsStorage
