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
from dotmpe.du.builder import Builder
import dotmpe.du.builder.dotmpe_v5
import dotmpe.du.builder.htdocs


class DuComponentLoaderMonkeyPatchTest(unittest.TestCase):

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

    """
    Test dotmpe.du.comp
    """

    def test_2_get_reader_class(self):
        for Reader, names in DuComponentLoaderMonkeyPatchTest.reader:
            for name in names:
            	self.assert_( issubclass(Reader, docutils.readers.Reader), 
            	        Reader )
                self.assertEquals( Reader, comp.get_reader_class(name) )

    def test_2_get_parser_class(self):
        for Parser, names in DuComponentLoaderMonkeyPatchTest.parser:
            for name in names:
            	self.assert_( issubclass(Parser, docutils.parsers.Parser),
            	        Parser )
                self.assertEquals( Parser, comp.get_parser_class(name) )

    def test_3_get_writer_class(self):
        for Writer, names in DuComponentLoaderMonkeyPatchTest.writer:
            for name in names:
            	self.assert_( issubclass(Writer, docutils.writers.Writer),
            	        Writer )
                self.assertEquals( Writer, comp.get_writer_class(name) )

    builder = (
            (dotmpe.du.builder.htdocs.Builder, ['dotmpe.du.builder.htdocs']),
            (dotmpe.du.builder.dotmpe_v5.Builder, ['dotmpe.du.builder.dotmpe_v5'])
        )
    def test_4_get_builder_class(self):
        for Builder, names in self.builder:
            for name in names:
                self.assertEquals(
                        dotmpe.du.comp.get_builder_class(name),
                        Builder )
                dotmpe.du.comp.get_builder_class(name)
            	self.assert_( issubclass(Builder, dotmpe.du.builder.Builder),
            	        Builder )

if __name__ == '__main__':
    unittest.main()

