# pylint: disable=no-member
"""
Utils to test re-writer, intended to be the reverse of the given parser.

Pylint should ignore AbstractTestCase members as these will be bound to the
test-runner instead.
"""
import os, re, unittest

from docutils.utils import SystemMessage
import dotmpe

import docutils.core
import os, re
import sys
import unittest
from StringIO import StringIO
from difflib import unified_diff
from pprint import pformat

from docutils.utils import SystemMessage

import init
import dotmpe.du.ext
from dotmpe.du.ext.writer.rst import Writer

import docutils.core
import os, re
import sys
import unittest
from StringIO import StringIO
from difflib import unified_diff
from pprint import pformat

from docutils.utils import SystemMessage

import dotmpe.du.ext
from dotmpe.du.ext.writer.rst import Writer



width = 79

class AbstractParserTestCase(object):

    DOC_FILE = None
    DOC_PXML_FILE = None

    TAG = None
    VERBOSE = 1

    corrupt_sources = []

    def _test_parser(self, parser, lossy=True):
        """Do comparison on trees generated from rST files.

        Tree comparison based on pseudoxml string (structure, attributes).
        Failure on mismatch, or errors during re-parsing.
        """

        try:
            self.__test_parser(parser, lossy=lossy)
        except SystemMessage, e:
            self.fail(e)

    def __test_parser(self, parser, lossy=True):
        global width

        doc = open(self.DOC_FILE).read().decode('utf-8')
        assert isinstance(doc, unicode), doc

        expected_pxml = open(self.DOC_PXML_FILE).read().decode('utf-8')

        self.assertNotEqual(doc.strip(), u'', "Empty test file. "+
                    ("on <%s>" % self.DOC_FILE ))

        if self.VERBOSE:
            print self.DOC_FILE.ljust(width,'=')

        ## Compare parse trees, using pprint/pseudoxml representation
        warnings = StringIO()
        generated_tree = docutils.core.publish_parts(
                source=doc,
                source_path=self.DOC_FILE,
                parser=parser,
                settings_overrides={
                    'warning_stream': warnings,
                    #'input_encoding': 'unicode',
                    #'output_encoding': 'unicode',
                    #'error_encoding': 'unicode',
                    #'error_encoding_error_handler': 'replace',
                    #'warnings': 'test.log',
                },
                writer_name='pprint')['whole']
        warnings = warnings.getvalue()

        # print unified diff for PXML mismatch
        diff = "\n".join(list(unified_diff(expected_pxml.split('\n'), generated_tree.split('\n'))))

        if self.VERBOSE:
            out = [u'']
            original_out = expected_pxml.strip().split('\n')
            generated_out = generated_tree.strip().split('\n')
            out += [ (u'Original Tree ').ljust(width, '-') +u' '+ (u'Generated Tree ').ljust(width, '-') ]
            while original_out or generated_out:
                p1 = u''
                p2 = u''
                if original_out:
                    p1 = original_out.pop(0)
                if generated_out:
                    p2 = generated_out.pop(0)
                out += [ p1.ljust(width) +u' '+ p2.ljust(width) ]
            out += [u'']
            diff += "\n".join(out)

#        if self.VERBOSE:
#            print diff

        self.assertEqual( expected_pxml, generated_tree,
                    "pxml tree mismatch \n "+
                    ("on <%s>" % self.DOC_FILE )+"\n\n"+
                    diff )

        if warnings:
            self.assertFalse(warnings.strip(),
                    "Error parsing test document\n "+
                    ("on <%s>" % self.DOC_FILE )+"\n\n"+
                    warnings)
        assert True

def new_parser_testcase(tag, testcase_name, doc_file, pxml_file, lossy=False):
    lossy_str = 'Lossy'
    if not lossy:
        lossy_str = 'Lossless'
    suffix = "%s%sParserTestCase" % (lossy_str, tag.title())
    parser_class = dotmpe.du.comp.get_parser_class(tag)
    class TestCase(unittest.TestCase, AbstractParserTestCase):
        DOC_FILE = doc_file
        DOC_PXML_FILE = pxml_file
        PARSER_CLASS = parser_class
        TAG = tag
        def runTest(self):
            self._test_parser(self.PARSER_CLASS(), lossy=lossy)
        runTest.__doc__ = "%s; %s doctree comparison; Parser '%s'" % (testcase_name, lossy_str, tag)
    TestCase.__name__ = testcase_name +suffix
    return TestCase



class AbstractWriterTestCase(object):

    DOC_FILE = None
    VERBOSE = 0
    corrupt_sources = ()

    def _test_writer(self, writer, lossy=True):
        """Do comparison on trees generated from rST files.

        Tree comparison based on pseudoxml string (structure, attributes).
        Failure on mismatch, or errors during re-parsing.
        """

        try:
            self.__test_writer(writer, lossy=lossy)
        except SystemMessage, e:
            self.fail(e)

    def __test_writer(self, writer, lossy=True):
        rst = open(self.DOC_FILE).read().decode('utf-8')
        if self.VERBOSE:
            print self.DOC_FILE.ljust(79,'=')

        self.assertNotEqual(rst.strip(), '', "Empty test file. "+
                    ("on <%s>" % self.DOC_FILE ))

        # Generate pseudoxml from source
        warnings = StringIO()
        original_tree = docutils.core.publish_parts(
                source=rst,
                source_path=self.DOC_FILE,
                #reader_name=self.TAG,
                settings_overrides={
                    'warning_stream': warnings,
#                    'output_encoding': 'unicode',
#                    'output_encoding': 'ascii',
                    #'input_encoding': 'unicode',
                },
                writer_name='pseudoxml')['whole']#writer_name='dotmpe-rst')
        warnings = warnings.getvalue()
        if warnings and self.DOC_FILE not in self.corrupt_sources:
            self.assertFalse(warnings.strip(), "Corrupt test source file: "+
                    ("on <%s>" % self.DOC_FILE )+"\n"+
                    warnings)
            return

        if self.VERBOSE:
            print " Original".ljust(79,'-')
            print original_tree

        # Publish the source file to rST, ie. regenerate the rST file
        warnings = StringIO()
        result = docutils.core.publish_parts(
                source=rst,
                source_path=self.DOC_FILE,
                #reader_name=reader_name,
                settings_overrides={
                    'warning_stream': warnings,
                    'input_encoding': 'unicode',
                },
                writer=writer)['whole']#writer_name='dotmpe-rst')
        if not lossy:
            self.assertEqual( result, rst,
                    ("on <%s>" % self.DOC_FILE )+"\n"+
                    rst+'\n'+(''.rjust(79,'='))+'\n'+result )

        self.assertNotEqual(result.strip(), '', "Empty generated file. "+
                    ("on <%s>" % self.DOC_FILE ))

        ## Compare parse trees, generate pseudoxml representation
        warnings = StringIO()
        generated_tree = docutils.core.publish_parts(
                source=result,
                source_path=self.DOC_FILE,
                #reader_name=reader_name,
                settings_overrides={
                    'warning_stream': warnings,
                    'input_encoding': 'unicode',
                },
                writer_name='pseudoxml')['whole']
        warnings = warnings.getvalue()
        if warnings:
            self.assertFalse(warnings.strip(), "Error re-parsing generated file\n "+
                    ("on <%s>" % self.DOC_FILE )+"\n\n"+
                    warnings)

        diff = "\n".join(list(unified_diff(original_tree.split('\n'), generated_tree.split('\n'))))

        self.assertEqual( original_tree, generated_tree,
                    "pxml tree mismatch \n "+
                    ("on <%s>" % self.DOC_FILE )+"\n\n"+
                    diff )
#                    original_tree+'\n'+(''.rjust(79,'='))+'\n'+generated_tree )

        if self.VERBOSE:
            print " Generated".ljust(79,'-')
            print generated_tree
            print

def new_writer_testcase(tag, testcase_name, doc_file, lossy=False):
    lossy_str = 'Lossy'
    if not lossy:
        lossy_str = 'Lossless'
    suffix = "%s%sWriterTestCase" % (lossy_str, tag.title())
    writer_class = dotmpe.du.comp.get_writer_class(tag)
    class TestCase(unittest.TestCase, AbstractWriterTestCase):
        DOC_FILE = doc_file
        TAG = tag
        def runTest(self):
            self._test_writer(writer_class(), lossy=lossy)
        runTest.__doc__ = "%s; %s doctree comparison; Writer '%s'" % (testcase_name, lossy_str, tag)
    TestCase.__name__ = testcase_name +suffix
    return TestCase


def mkclassname(filename):
    assert isinstance(filename, basestring), filename
    name = os.path.splitext(os.path.basename(filename))[0].replace('.','_')
    name = name.replace('-', ' ').title().replace(' ','').replace('+','_')
    if name[0].isdigit():
        name = '_'+name
    assert re.match('^[A-Za-z_][A-Za-z0-9_]+$', name), (name, filename)
    return name



def print_compare_writer(doc_file,
        writer_name='rst', writer_class=None,
        reader_name='mpe', reader_class=None,
        parser_name='rst', parser_class=None,
        max_width=158, encoding='utf-8'):

    """
    Print a side by-side view of the document, source, and re-written version.
    """
    import docutils.core, dotmpe

    out = []
    out += [ (' ' + doc_file).rjust(max_width, '=')]
    doc = open(doc_file).read().decode(encoding)
    assert isinstance(doc, unicode), doc

    if not reader_class:
        #reader_class = dotmpe.du.ext.reader.get_reader_class(reader_name)
        reader_class = dotmpe.du.comp.get_reader_class(reader_name)
    if not parser_class:
        parser_class = dotmpe.du.comp.get_parser_class(parser_name)

    original_tree = docutils.core.publish_parts(
            reader=reader_class(parser_class()),
            source=doc,
            writer_name='pseudoxml',
            settings_overrides={'input_encoding':'utf-8'})['whole']
    assert isinstance(original_tree, unicode)
    result = docutils.core.publish_parts(
            reader=reader_class(parser_class()),
            source=doc,
            writer=writer_class())['whole']
    assert isinstance(result, unicode)
    try:
        generated_tree = docutils.core.publish_parts(
                source=result,
                writer_name='pseudoxml')['whole']
    except Exception, e:
        generated_tree = u''
    assert isinstance(generated_tree, unicode)

    width = int((max_width-1)/2)
    #if width > 79:
    #    width = 79

    #if width >= max_width*2+1:

    original_out = original_tree.strip().split('\n')
    generated_out = generated_tree.strip().split('\n')
    out += [ (u'Original Tree ').ljust(width, '-') +u' '+ (u'Generated Tree ').ljust(width, '-') ]
    while original_out or generated_out:
        p1 = u''
        p2 = u''
        if original_out:
            p1 = original_out.pop(0)
        if generated_out:
            p2 = generated_out.pop(0)
        out += [ p1.ljust(width) +u' '+ p2.ljust(width) ]
    out += [u'']

    # print side-by-side view
    original_out = doc.strip().decode('utf-8').split('\n')
    generated_out = result.strip().decode('utf-8').split('\n')
    out += [ (u'Original ').ljust(width, '-') +u' '+ (u'Rewriter ').ljust(width, '-') ]
    while original_out or generated_out:
        p1 = u''
        p2 = u''
        if original_out:
            p1 = original_out.pop(0)
        if generated_out:
            p2 = generated_out.pop(0)
        # TODO: wrap lines
        #if len(p1) > width or len(p2) > width:
        out += [ p1.ljust(width) +u' '+ p2.ljust(width) ]
    out += [u'']

    #else:

    #    out += [ ('Original ').ljust(width, '-') ]
    #    out += [ doc.strip(), u'']

    #    out += [ ('Generated ').ljust(width, '-') ]
    #    out += [ result.strip(), u'' ]

    out += [ ('Result ').ljust(max_width, '-')]
    listwidth = int(width * 0.25)
    out += [ 'File:'.rjust(listwidth, ' ') +' '+ doc_file ]
    if generated_tree == original_tree:
        out += [ 'Doctree Comparison:'.rjust(listwidth, ' ') +" PXML match" ]
        out += [ 'Source Comparison:'.rjust(listwidth, ' ') +' '+ \
                ((doc == result) and "Lossless" or "Lossy")]
    else:
        out += [ 'Doctree Comparison:'.rjust(listwidth, ' ') +" Error: PXML mismatch" ]
    out += [u'']

    print u"\n".join(out)


