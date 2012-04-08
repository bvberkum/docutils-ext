"""
Reader/Parser tests for Atlassian Confluence documents
(atlassian confluence wiki format).

- confluence to pxml (parse; lossy)

The 'confluence-embedded' format should parse confluence to du raw nodes of
format 'confluence'.
"""
import sys

import dotmpe.du.ext.writer

import init
from util import mkclassname, new_parser_testcase, new_writer_testcase


def create_parser_test(files):
    """
    Test confluence reading/parser.

    - Parse confluence, and write pxml tree.

    * Compare generated pxml with expected pxml.
    """
    for acw_file, pxml_file in files:
        testcase_name = mkclassname(acw_file)

        # Lossy, src2pxml, expected pxml compare
        TestCase = new_parser_testcase('confluence-mpe', testcase_name, acw_file,
                pxml_file, True)
        TestCase.__module__ = __name__
        setattr(sys.modules[__name__], testcase_name, TestCase)


create_parser_test(init.ACW_DOC)

