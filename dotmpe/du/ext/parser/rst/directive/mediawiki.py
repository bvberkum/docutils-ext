"""
This is a very simple directive to parse mediawiki formatted content embedded in
Docutils documents. The content is always published to a raw HTML node.

https://maze.io/2009/10/22/rendering-mediawiki-markup-in-restructuredtext/
"""
from docutils.parsers.rst import Directive
try:
    import xml.etree.ElementTree as ET
except:
    from elementtree import ElementTree as ET

from mwlib.dummydb import DummyDB
from mwlib.uparser import parseString
from mwlib.xhtmlwriter import MWXHTMLWriter, preprocess


class MediaWiki(Directive):

    required_arguments = 0
    optional_arguments = 1
    has_content = True
    option_spec = {}

    def run(self):
        raw = u'\n'.join(self.content)
        # empty wikidb
        db = DummyDB()
        # run parser and pre-processors
        parsed = parseString(title='Export', raw=raw, wikidb=db)
        preprocess(parsed)
        # write XHTML
        xhtml = MWXHTMLWriter()
        xhtml.writeBook(parsed)
        # remove the H1 heading (title) from the document
        article = xhtml.xmlbody.getchildren()[0]
        article.remove(article.getchildren()[0]) # remove caption
        # render to string
        block = ET.tostring(xhtml.xmlbody)
        return [nodes.raw('', block, format='html')]

