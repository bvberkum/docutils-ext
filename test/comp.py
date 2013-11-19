import unittest

import docutils

from dotmpe.du import comp
from dotmpe.du.ext.reader import \
        mpe, mkdoc
from dotmpe.du.ext.parser import \
        atlassian as atlassian_parser, \
        simplereader
#        rst as rst_parser,  \
from dotmpe.du.ext.writer import \
        atlassian as atlassian_writer,  \
        formresults, html, \
        rst as rst_writer, pydoc, latex2e, xhtml, \
        htmlform



class DuComponentLoaderMokeyPatchTest(unittest.TestCase):

    reader = (
    	    ( mpe.Reader, ('mpe', 'mpe-mpe',) ),
    	    ( mkdoc.Reader, ('mkdoc', 'mkdoc-mpe',)) ,
        )
    def test_1_get_reader_class(self):
        for Reader, names in self.reader:
            for name in names:
                self.assertEquals( Reader, 
                        docutils.readers.get_reader_class(name) )

    parser = (
#            ( atlassian_parser.Parser, ('atlassian', 'atlassian-mpe') ),
#            ( rst_parser.Parser, ('rst', 'rst-mpe') )
        )
    def test_2_get_parser_class(self):
        for Parser, names in self.parser:
            for name in names:
                self.assertEquals( Parser, 
                        docutils.parsers.get_parser_class(name) )

    writer = (
            ( html.Writer, ('html', 'html-mpe') ),
            ( xhtml.Writer, ('xhtml', 'xhtml-mpe') ),
            ( rst_writer.Writer, ('rst', 'rst-mpe') ),
#            ( pydoc.Writer, ('pydoc', 'pydoc-mpe') ),
            ( latex2e.Writer, ('latex2e', 'latex2e-mpe') ),
            ( htmlform.Writer, ('html-form', 'html-form-mpe') ),
            ( formresults.Writer, ('formresults', 'formresults-mpe') ),
            ( atlassian_writer.Writer, ('atlassian', 'atlassian-mpe') ),
        )
    def test_3_get_writer_class(self):
        for Writer, names in self.parser:
            for name in names:
                self.assertEquals( Writer, 
                        docutils.writers.get_writer_class(name) )


class DotmpeComponentLoaderTest(unittest.TestCase):

    def test_2_get_reader_class(self):
        for Reader, names in DuComponentLoaderMokeyPatchTest.reader:
            for name in names:
            	self.assert_( issubclass(Reader, docutils.readers.Reader), 
            	        Reader )
                self.assertEquals( Reader, comp.get_reader_class(name) )

    def test_2_get_parser_class(self):
        for Parser, names in DuComponentLoaderMokeyPatchTest.parser:
            for name in names:
            	self.assert_( issubclass(Parser, docutils.parsers.Parser),
            	        Parser )
                self.assertEquals( Parser, comp.get_parser_class(name) )

    def test_3_get_writer_class(self):
        for Writer, names in DuComponentLoaderMokeyPatchTest.parser:
            for name in names:
            	self.assert_( issubclass(Writer, docutils.writers.Writer),
            	        Writer )
                self.assertEquals( Writer, comp.get_writer_class(name) )

if __name__ == '__main__':
    unittest.main()

