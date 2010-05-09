"""
A would be inline scanner.
This is nowhere near finished. Duck-tape and moving parts follow, keep clear ;)
"""
import urlparse
from docutils import nodes
from nabu import extract
from dotmpe.du.ext import extractor



class InlineExtractor(extract.Extractor):

    """
    Extract specific text roles and parse the node's content. The resulting
    structure may replace the original, while any extracted data is passed to
    the store.

    Standard Du does not have inline nesting yet, but the nodes content could
    include other inline nodes using the `nested` branch.

    This provides alternative option to the PEP and RFC inline reference parsing
    in Du core.
    """

    default_inline_roles = (
            'title-reference', 'strong', 'emphasis', 'literal'
        )
    "Other roles may be defined in the document."

    settings_spec = ((
             'Extract inline. Multiple allowed.',
             ['--extract-inline'],
             {'metavar':'ROLE:parser[,ROLE:parser]', 'validator': util.multichoice(inlines),
              'action': 'append'}
            ), (
             'Parameters for use by storage component.',
             ['--inline-storage'],
             {'metavar':'ROLE:parser:parameters[,]'}
            ))

    default_priority = 900

    def apply(self, unid=None, store=None, **kwargs):
        v = self.Visitor(self.document)
        v.x = self
        self.document.walk(v)

    class Visitor(nodes.SparseNodeVisitor):

        def visit_title_reference(self, node):
            print node.attributes
            #self.x.storage.store()

        def visit_emphasis(self, node):
            pass

        def visit_strong(self, node):
            pass

        def visit_inline(self, node):
            pass

        def visit_literal(self, node):
            pass


# Storage types

#class InlineExtractorStorage(extractor.ParametrizedStorage):
#    # XXX: class ParametrizedStorage(extract.ExtractorStorage)?
#    def set_parameters(self, paramstring):
#        pass


class TransientInlineExtractorStorage(InlineExtractorStorage):
    " "


try:

    from google.appengine.ext import db

except ImportError, e:
    if 'logging' in globals():
        globals()['logging'].info('Not loading GAE reference model.')

else:

    class GAEInlineExtractorStorage(extract.ExtractorStorage):
        def store(self, unid, *args):
            pass

        def clear(self, unid=None):
            pass

        def reset_schema(self):
            raise Exception, 'TODO: reset_schema(%s)'%repr(self)


## Role parsers


