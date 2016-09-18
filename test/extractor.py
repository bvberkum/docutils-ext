"""

Builder
    Reader
        extractor_spec
            ..
        extractors = ( ( extractor, storage ), )
            ..
    Parser
        ..
    Writer
        ..
    components = ( reader, parser, writer )

"""

import unittest

from docutils import readers, parsers, writers

import dotmpe.du
from dotmpe.du import builder
#from dotmpe.du.ext import reader, parser, writer


class Builder(builder.Builder):

    class Reader(readers.Reader):
        settings_spec = (
            'My Reader', 
            None,
            () #form.FormProcessor.settings_spec + ()
        )

class ExtractorTest(unittest.TestCase):

    def test__extractor_spec(self):
        builder = Builder()
        builder.prepare()
        #assert builder.stores['']


if __name__ == '__main__':
    unittest.main()

