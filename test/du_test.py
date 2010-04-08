import docutils.core
import unittest

import init
import dotmpe.du.ext
from dotmpe.du.ext.writer.rst import Writer


class RstWriter(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_all(self):
		# XXX: better do 'lossless' comparison on tree's, ie reparse output rst
		for doc in init.TEST_DOC:
			print (' ' + doc).rjust(79, '=')
			rst = open(doc).read()
			#print (rst, )

			print ' pseudoxml'.rjust(79, '-')
			result = docutils.core.publish_parts(source=rst, 
					writer_name='pseudoxml')['whole']#writer_name='dotmpe-rst')
			print result

			print ' Sefan\'s branch'.rjust(79, '-')
			result = docutils.core.publish_parts(source=rst, 
					writer=init.LOSSLESS_WRITER.Writer())['whole']#writer_name='dotmpe-rst')
			#print (result, )
			print "Lossless: ",rst == result

			#print ' Own development'.rjust(79, '-')
			result = docutils.core.publish_parts(source=rst, 
					writer=Writer())['whole']#writer_name='dotmpe-rst')
			#print (result, )
			#print "Lossless: ",rst == result
			self.assertEqual(rst, result)

			print (' ' + doc + ' END').rjust(79, '='), '\n'

	
