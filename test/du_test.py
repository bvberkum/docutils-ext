import docutils
import unittest
import dotmpe.du.ext
import init


class RstWriter(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_1(self):
		for doc in init.TEST_DOC:
			rst = open(doc).read()
			parts = docutils.core.publish_parts(source=rst, writer_name='dotmpe-rst')
			print parts


