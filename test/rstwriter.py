import docutils.core
import unittest

import init
import dotmpe.du.ext
from dotmpe.du.ext.writer.rst import Writer


class RstWriterTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_all(self):
        # XXX: do comparison on tree's, ie reparse output rst too
        # XXX: using writer alias is preferred above importing the class here
        print
        for doc in init.TEST_DOC:
            print (' ' + doc).rjust(70, '=')
            rst = open(doc).read()
            #print (rst, )

            #print ' tree'.rjust(70, '-')
            original_tree = docutils.core.publish_parts(
                    source=rst, 
                    writer_name='pseudoxml')['whole']#writer_name='dotmpe-rst')
            #print original_tree

            ### Parse and re-produce rSt, lossless-branch
            print ' Sefan\'s branch'.rjust(70, '-')
            result = docutils.core.publish_parts(
                    source=rst, 
                    writer=init.LOSSLESS_WRITER.Writer())['whole']#writer_name='dotmpe-rst')
            #print (result, )
            print "Lossless: ",rst == result

            ## Compare parse trees
            result_tree = docutils.core.publish_parts(
                    source=result,
                    writer_name='pseudoxml')['whole']

            print "Equal doctree: ", original_tree == result_tree


            ### Parse and re-produce rSt, but non-lossless, ie. without complete 
            # whitespace and character equavalence but same textual and
            # structural

            print ' Own development'.rjust(70, '-')
            result = docutils.core.publish_parts(
                    source=rst, 
                    writer=Writer())['whole']#writer_name='dotmpe-rst')
            #print (result, )
            print "Lossless: ",rst == result
            #self.assertEqual(rst, result)

            ## Compare parse trees
            generated_tree = docutils.core.publish_parts(
                    source=result,
                    writer_name='pseudoxml')['whole']
            print "Equal doctree: ", original_tree == generated_tree

            #print (' ' + doc + ' END').rjust(70, '='), '\n'
            print (' END').rjust(70, '='), '\n'

