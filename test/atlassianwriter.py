import sys

import dotmpe.du.ext.parser
#print dotmpe.du.ext.parser.
#from dotmpe.du.ext.writer.rst import Writer

import init
from util import mkclassname, new_parser_testcase


def create_tests(files):

    for acw_file in files:
        testcase_name = mkclassname(acw_file)

        # Lossy
        TestCase = new_parser_testcase('atlassian-mpe', testcase_name, acw_file, True)
        TestCase.__module__ = __name__
        setattr(sys.modules[__name__], testcase_name, TestCase)
  

create_tests(init.ACW_DOC)

