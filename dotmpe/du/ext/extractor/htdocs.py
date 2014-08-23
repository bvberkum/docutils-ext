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

from nabu import extract

from docutils import nodes
#from dotmpe.du.ext import extractor

from script_mpe import taxus
from script_mpe.taxus.init import SqlBase
from script_mpe.taxus.util import get_session



class HtdocsExtractor(extract.Extractor):

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


class HtdocsStorage(extract.ExtractorStorage):

    """
    Work in progress: SQLAlchemy storage
    """

    def __init__(self, dbref=None):
        assert dbref, ("Missing SQL-alchemy DB ref", self)
        self.session = get_session(dbref, True)

    def store(self, source_id, *args):
        pass

    def clear(self, source_id):
        pass

    def reset_schema(self):
        raise Exception("NotImplemented")

    # custom
    def find_term(self, term):
        t = Table('titles', SqlBase.metadata, autoload=True)#, autoload_with=engine)
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

