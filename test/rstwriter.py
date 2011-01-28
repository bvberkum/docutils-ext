import docutils.core
import unittest
from StringIO import StringIO

from docutils.utils import SystemMessage

import init
import dotmpe.du.ext
from dotmpe.du.ext.writer.rst import Writer



class AbstractRstWriterTestCase(unittest.TestCase):

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
        self.assertEqual( original_tree, generated_tree, 
                    "pxml tree mismatch \n "+
                    ("on <%s>" % self.RST_FILE )+"\n\n"+
                    original_tree+'\n'+(''.rjust(79,'='))+'\n'+generated_tree )

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

    
