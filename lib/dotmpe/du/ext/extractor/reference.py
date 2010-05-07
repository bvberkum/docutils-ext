"""
Back `in 2004 there was a great post`__ on the mailing list about handling of
references in docutils. 

.. __: http://thread.gmane.org/gmane.text.docutils.devel/2060/focus=2066

"""
import urlparse
from docutils import nodes
from nabu import extract


class Extractor(extract.Extractor):
    """
    Stores all external references in an index.
    """
    default_priority = 900

    def apply(self, unid=None, store=None, **kwargs):
        v = self.Visitor(self.document)
        v.x = self
        self.document.walk(v)

    class Visitor(nodes.SparseNodeVisitor):

        def visit_reference(self, node):
            if 'refuri' in node.attributes:
                link = node.attributes['refuri']
                scheme, d,p,r,q,f = urlparse.urlparse(link)
                if scheme in ('sip', 'mailto', 'ssh'):
                    return
                self.x.storage.store(self.x.unid, link)
                

## App-engine storage

try:

    from google.appengine.ext import db

except ImportError, e:
    pass#print 'Not loading GAE reference model.'

else:

    class Reference(db.Model):
        url = db.LinkProperty()
        unid = db.StringProperty()

    class ReferenceStorage(extract.ExtractorStorage):
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
            raise Exception, 'reset_schema'+repr(self)


