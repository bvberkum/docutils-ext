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




class AbstractRstWriterTestCase(object):#unittest.TestCase):

    RST_FILE = None
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
        rst = open(self.RST_FILE).read()
        if self.VERBOSE:
            print self.RST_FILE.ljust(79,'=')

        self.assertNotEqual(rst.strip(), '', "Empty test file. "+
                    ("on <%s>" % self.RST_FILE ))

        # Generate pseudoxml from source
        warnings = StringIO()
        original_tree = docutils.core.publish_parts(
                source=rst, 
                settings_overrides={'warning_stream':warnings},
                writer_name='pseudoxml')['whole']#writer_name='dotmpe-rst')
        warnings = warnings.getvalue()
        if warnings and self.RST_FILE not in self.corrupt_sources:
            self.assertFalse(warnings.strip(), "Corrupt test source file: "+
                    ("on <%s>" % self.RST_FILE )+"\n"+
                    warnings)
            return

        if self.VERBOSE:
            print " Original".ljust(79,'-')
            print original_tree

        # Publish the source file to rST, ie. regenerate the rST file
        warnings = StringIO()
        result = docutils.core.publish_parts(
                source=rst, 
                settings_overrides={'warning_stream':warnings},
                writer=writer)['whole']#writer_name='dotmpe-rst')
        if not lossy:
            self.assertEqual( result, rst, 
                    ("on <%s>" % self.RST_FILE )+"\n"+
                    rst+'\n'+(''.rjust(79,'='))+'\n'+result )

        self.assertNotEqual(result.strip(), '', "Empty generated file. "+
                    ("on <%s>" % self.RST_FILE ))

        ## Compare parse trees, generate pseudoxml representation
        warnings = StringIO()
        generated_tree = docutils.core.publish_parts(
                source=result,
                settings_overrides={'warning_stream':warnings},
                writer_name='pseudoxml')['whole']
        warnings = warnings.getvalue()
        if warnings:
            self.assertFalse(warnings.strip(), "Error re-parsing generated file\n "+
                    ("on <%s>" % self.RST_FILE )+"\n\n"+
                    warnings)

        diff = "\n".join(list(unified_diff(original_tree.split('\n'), generated_tree.split('\n'))))

        self.assertEqual( original_tree, generated_tree, 
                    "pxml tree mismatch \n "+
                    ("on <%s>" % self.RST_FILE )+"\n\n"+
                    diff )
#                    original_tree+'\n'+(''.rjust(79,'='))+'\n'+generated_tree )

        if self.VERBOSE:
            print " Generated".ljust(79,'-')
            print generated_tree
            print


class LossyRstWriterTest(AbstractRstWriterTestCase):

    #def test_dotmpe_doctree_pxml(self):
    def runTest(self):
        "Lossy doctree comparison for ``dotmpe.du.ext.rst.writer`` "

        self._test_writer(Writer())

    #def test_lossless_branch(self):
    #    "Lossy doctree comparison for lossless-branch "

    #    self._test_writer(init.LOSSLESS_WRITER.Writer())


class LosslessRstWriterTest(AbstractRstWriterTestCase):

    def test_dotmpe_doctree_pxml(self):
        "Lossless doctree comparison for ``dotmpe.du.ext.rst.writer`` "

        self._test_writer(Writer(), False)

    def test_lossless_branch(self):
        "Lossless doctree comparison for lossless-branch "

        self._test_writer(init.LOSSLESS_WRITER.Writer(), False)



def new_rstwriter_testcase(testcase_name, rst_file, lossy=False):
    if lossy:
        class TestCase(LossyRstWriterTest, unittest.TestCase):
            RST_FILE = rst_file
        TestCase.__name__ = testcase_name +'LossyRstWriterTestCase'
    else:
        class TestCase(LosslessRstWriterTest, unittest.TestCase):
            RST_FILE = rst_file
        TestCase.__name__ = testcase_name +'LosslessRstWriterTestCase'
    return TestCase


def mkclassname(filename):
    name = os.path.splitext(os.path.basename(filename))[0].replace('.','_')
    name = name.replace('-', ' ').title().replace(' ','').replace('+','_')
    if name[0].isdigit():
        name = '_'+name
    assert re.match('^[A-Za-z_][A-Za-z0-9_]+$', name), (name, filename)
    return name

def create_tests(files):
    for rst_file in files:
    
        testcase_name = mkclassname(rst_file)

        # Lossy
        TestCase = new_rstwriter_testcase(testcase_name, rst_file, True)
        if rst_file.endswith('demo.rst'):
            TestCase.corrupt_sources = [rst_file]
        setattr(sys.modules[__name__], testcase_name, TestCase)

        # Lossless

# XXX:BVB: reinstate lossless tests
        #TestCase = new_rstwriter_testcase(testcase_name, rst_file, False)
        #if rst_file.endswith('demo.rst'):
        #    TestCase.corrupt_sources = [rst_file]
        #setattr(sys.modules[__name__], testcase_name, TestCase)


