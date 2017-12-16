"""
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
from dotmpe.du.util import SqlBase, get_session
from dotmpe.du.ext import extractor


logger = util.get_log(__name__, fout=False)

logger = util.get_log(__name__)

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
             'Database to store references. ',
             ['--reference-database'],
             {
                 'metavar':'PATH',
                 'validator': util.optparse_init_anydbm,
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
        ),)
    )

    default_priority = 900

    def apply(self, unid=None, store=None, **kwargs):
        v = RefVisitor(self.document)
        self.document.walk(v)

        refdb = getattr(self.document.settings, 'reference_database', None)
        if refdb == None:
            return
        v = RefDbVisitor(self.document)
        self.document.walk(v)
        refdb.close()


class RefVisitor(nodes.GenericNodeVisitor):

    def default_visit(self, node):
        """Override for generic, uniform traversals."""
        if not hasattr(node, 'attributes'):
            return
        if 'refuri' in node.attributes:
            link = node.attributes['refuri']
            logger.debug("Found uriref %s", link)


    def default_departure(self, node):
        """Override for generic, uniform traversals."""


class RefDbVisitor(nodes.SparseNodeVisitor):

    """
    """

    def visit_reference(self, node):
        if 'refuri' in node.attributes:
            link = node.attributes['refuri']
            logger.debug("Found uriref %s", link)
            #scheme, d,p,r,q,f = urlparse.urlparse(link)
            #if scheme in ('sip', 'mailto', 'ssh'):
            #    return
            #self.store(node)

    def store(self, node):

        refdb = self.document.settings.reference_database
        ctx = self.document.settings.reference_context
        link = node.attributes['refuri']
        if not isinstance(link, unicode):
            link = unicode(link)

        if not uriref.scheme.match(link):
            # Allow site-wide absolute paths:
            if not os.path.exists(link) and link.startswith(os.sep):
                link = link[1:]
            if link.startswith('~'):
                link = os.path.expanduser(link)
            if not os.path.exists(link):
                self.document.reporter.warning(
                    "Reference %s does not provide an explicit scheme, but is "
                    "also not a local path. " % (link))
                return
            if ctx:
                link = ctx + link
            else:
                link = "file://%s%s" % (socket.gethostname(),
                        os.path.abspath(os.path.normpath(link)))

        key = link.encode('utf-8')
        if key in refdb:
            #node.childnodes.append(nodes..)
            self.document.reporter.warning("Duplicate reference to %s" % link)
        else:
            refdb[key] = pickle.dumps({'name':node.get('name'),'href':link})


class ReferenceStorage(extractor.SQLiteExtractorStorage):

    sql_relations_unid = []
    sql_relations = []

    def __init__(self, session=None, dbref=None, initdb=False):
        if not session:
            assert dbref, ( dbref, initdb )
            # set for SA, get engine to use as DBAPI-2.0 compatible connection
            self.session = get_session(dbref, True)
            self.connection = SqlBase.metadata.bind.raw_connection()
        else:
            self.session = session
        # XXX can I get raw-connection from self.session?
        #self.connection = SqlBase.metadata.bind.raw_connection()
        #logger.info("Connected to %s", self.connection)
        logger.info("Extractor store to %s", self.session)

    def store(self, source_id, *args):
        print 'store', source_id, args

    def clear(self, source_id):
        pass


Extractor = ReferenceExtractor
Storage = ReferenceStorage



## App-engine storage

# XXX: Currently unused code
try:

    from google.appengine.ext import db

except ImportError, e:
    pass#print 'Not loading GAE reference store.'

else:

    class Reference(db.Model):
        url = db.LinkProperty()
        unid = db.StringProperty()

    class ReferenceStorage(extractor.ExtractorStorage):
        def store(self, unid, url):
            ref = Reference()
            ref.unid = unid
            ref.url = url
            ref.put()

        def clear(self, unid=None):
            if unid:
                refs = Reference.gql('WHERE unid = :1', unid).fetch(1)
            else:
                refs = Reference.all().fetch(1000)

            if refs:
                for ref in refs:
                    ref.delete()

        def reset_schema(self):
            raise Exception( 'reset_schema'+repr(self) )


## Maintenance?

class RefDbOptionParser(frontend.OptionParser):
    standard_config_files = []
    settings_spec = Extractor.settings_spec

def run_refdb_cli():
    # No help, just initalize refdb
    prsr = RefDbOptionParser()
    settings = prsr.parse_args()
    refdb = settings.reference_database
    if refdb:
        # Iter contents
        for link in refdb:
            print link, pickle.loads(refdb[link])
    else:
        import sys
        print >>sys.stderr, "No references"

if __name__ == '__main__':
    run_refdb_cli()

