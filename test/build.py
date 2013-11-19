"""
Builder class testing
"""
import os
import unittest

import docutils

import dotmpe.du
from dotmpe.du.builder import Builder


class DotmpeDuExtBuilderTest(unittest.TestCase):

    def test_x_prepare_source(self):
        builder = Builder()

        SOURCE = "this is a test source"
        self.assert_( not os.path.exists(SOURCE) )

        self.assertRaises( AssertionError, builder.prepare_source, None, )
        self.assertRaises( AssertionError, builder.prepare_source, None, None)
        self.assertRaises( AssertionError, builder.prepare_source, '', None)
        self.assertRaises( AssertionError, builder.prepare_source, '', '')
        clss, prsr, rdr, sttngs = builder.prepare_source(SOURCE)
        self.assertEquals(builder.source_class, docutils.io.StringInput)
        clss, prsr, rdr, sttngs = builder.prepare_source(SOURCE, "<id>")
        self.assertEquals(builder.source_class, docutils.io.StringInput)
        self.assertEquals(builder.source_id, "<id>")
        self.assertRaises( AssertionError, builder.prepare_source, 
                docutils.nodes.document("", ""))
        clss, prsr, rdr, sttngs = builder.prepare_source(
                docutils.nodes.document("", ""), "<id>")
        self.assertEquals(builder.source_class, docutils.io.DocTreeInput)

        testfn = '/tmp/testfn'
        try:
            os.utime(testfn, None)
        except:
            open(testfn, 'a').close()

        clss, prsr, rdr, sttngs = builder.prepare_source(testfn)
        self.assertEquals(builder.source_id, testfn)
        self.assertEquals(builder.source_class, docutils.io.FileInput)

        clss, prsr, rdr, sttngs = builder.prepare_source(testfn, True)
        self.assertEquals(builder.source_id, testfn)
        self.assertEquals(builder.source_class, docutils.io.FileInput)

        clss, prsr, rdr, sttngs = builder.prepare_source(None, testfn)
        self.assertEquals(builder.source_id, testfn)
        self.assertEquals(builder.source_class, docutils.io.FileInput)


if __name__ == '__main__':
    unittest.main()


