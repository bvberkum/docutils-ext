from docutils import nodes
from dotmpe.du.ext.writer import xhtml


class HTMLTranslator(xhtml.HTMLTranslator):

    def __init__(self, document):
        xhtml.HTMLTranslator.__init__(self, document)


class Writer(xhtml.Writer):

    def __init__(self):
        xhtml.Writer.__init__(self)
        self.translator_class = HTMLTranslator

