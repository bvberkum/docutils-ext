"""
Embedded Atlassian Confluence support for standard Docutils.

* Writer for Confluence markup which writes from raw node for
  'confluence-mebedded' format.

TODO
    - Support raw confluence with rST raw directive.
"""
import docutils
from docutils import frontend, nodes, writers


class Writer(writers.Writer):

    supported = ( 'confluence-embedded', )

    def __init__(self):
        writers.Writer.__init__(self)

    def translate(self):
        # XXX: output-format == confluence
        visitor = EmbeddedConfluenceTranslator(self.document)
        self.document.walkabout(visitor)

        self.output = visitor.astext()


class EmbeddedConfluenceTranslator(nodes.NodeVisitor):
    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        self.body = []

    def unknown_visit(self, node): pass
    def unknown_departure(self, node): pass
    
    def astext(self):
        return "\n".join(self.body)
