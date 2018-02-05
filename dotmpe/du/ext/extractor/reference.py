"""
:Created: 2010-05-09

..

    TODO: migrate core functions to dotmpe.du.ext.transform.reference,
    and base this extractor on that. See also htdocs extractor.

Back `in 2004 there was a nice post`__ on the mailing list about handling of
references in docutils.

.. __: http://thread.gmane.org/gmane.text.docutils.devel/2060/focus=2066

1. If no scheme.

   1. Try local path
   2. If absolute, remove root and try again.
   3. If not endswith extension, try default.

2. If scheme.

   1. Try and find protocol resolver
   2. Resolve resource and note Status, Locator and ID.

"""
import os, pickle, socket, urlparse

from docutils import nodes, frontend

import uriref
from dotmpe.du import util
from dotmpe.du.mpe_du_util import SqlBase, get_session
from dotmpe.du.ext import extractor, transform


logger = util.get_log(__name__, fout=False)


class ReferenceExtractor(extractor.Extractor):

    """
    Stores all external references in an index.
    """

    settings_spec = (
        'Reference Extractor Options',
        """The reference extractor analyzes URLs from the document, and classes
them into four types: external references for other domains, local references
for inter-document links, and two uncovered rest groups: query/fragment
references in the same protocol, and other sorts of URI which do not dereference
into a document. E.g. mailto.

References can result from several document syntax structures. Inline URL's,
hyperlink reference targets, image onclick targets. Inline code is not covered,
ie. raw HTML, script.

""",
        ((
             """Turn on external reference extraction. External references are
""",
             ['--external-refs'],
             {
                 'metavar': 'SPEC'
             }
        ),(
             'Turn on local inter-document reference extraction. ',
             ['--cross-refs'],
             {
                 'metavar': 'SPEC'
             }
        ),(
             'Extract both external local and external reference extraction. ',
             ['--all-refs'],
             {
                 'metavar': 'SPEC'
             }
        ),(
            'Resolve: request, take note of abnormal status, otherwise '
            'use identifier or update locator. ',
             ['--resolve-references'],
             {
                 'action': 'store_true'
             }
        ),(
            'Reference context to use in globalizing relative references. '
            'The default is to interpret all relative references as local '
            'file system paths, ',
             ['--reference-context'],
             {
                 'metavar': 'URI',
                 'validator': util.validate_context,
             }
        ),(
             'Dont run reference extractor, even if dbref is given. ',
             ['--no-reference'], { 'action': 'store_true' }
        ),)
    )

    default_priority = 900

    def apply(self, unid=None, store=None, **kwargs):

        g = self.document.settings
        if not g.no_db and not g.no_reference:
            v = transform.reference.RefVisitor(self.document)

            g = self.document.settings
            #g.dbref = taxus.ScriptMixin.assert_dbref(g.dbref)
            v.session = self.session = get_session(g.dbref)

            self.document.walk(v)


class ReferenceStorage(extractor.SQLiteExtractorStorage):

    sql_relations_unid = []
    sql_relations = []

    def __init__(self, session=None, dbref=None, initdb=False):
        self.session = session
        #if not session:
        #    assert dbref, ( dbref, initdb )
        #    # set for SA, get engine to use as DBAPI-2.0 compatible connection
        #    self.session = get_session(dbref, True)
        #    self.connection = SqlBase.metadata.bind.raw_connection()
        # XXX can I get raw-connection from self.session?
        #self.connection = SqlBase.metadata.bind.raw_connection()
        #logger.info("Connected to %s", self.connection)
        logger.info("Extractor store to %s", self.session)

    def store(self, source_id, *args):
        #taxus.htd.TNode.filter( ( TNode.global_id == prefix_path  ))
        print 'store', source_id, args

    def clear(self, source_id):
        pass


Extractor = ReferenceExtractor
Storage = ReferenceStorage
