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

	def test_1(self):
		for doc in init.TEST_DOC:
			rst = open(doc).read()
			result = docutils.core.publish_parts(source=rst, 
					writer_name='pseudoxml')['whole']#writer_name='dotmpe-rst')
			print result
			result = docutils.core.publish_parts(source=rst, 
					writer=Writer())['whole']#writer_name='dotmpe-rst')

			print result
			print rst == result


