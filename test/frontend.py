"""
dotmpe.du.frontend Module tests
"""

import sys
from cStringIO import StringIO
import unittest

from docutils import readers, parsers, writers

import dotmpe.du
from dotmpe.du import builder, frontend


class Builder(builder.Builder):

    class Reader(readers.Reader):
        settings_spec = (
            'My Reader', 
            "My Description",
            () 
        )


class FrontendTest(unittest.TestCase):

    def test__cli_process_1_help(self):

        """
        Tests wether builder picks up custom reader settings-spec on --help
        """

        out, sys.stdout = sys.stdout, StringIO()
        #  Maybe parse output again. 
        # TODO: Verify My Reader is in there
        try:
            builder = Builder()
            self.assertRaises( SystemExit,
                frontend.cli_process,
                    ['--help'],
                    builder=builder)
        except Exception, e:
            pass
        sys.stdout.seek(0)
        output = sys.stdout.read()
        sys.stdout = out

        assert 'My Reader' in output
        assert 'My Description' in output



if __name__ == '__main__':
    unittest.main()


