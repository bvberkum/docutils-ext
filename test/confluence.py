"""
Tests for Atlassian Confluence documents
(atlassian confluence wiki format).

- confluence to pxml (parse; lossy)
- rST to confluence (write; lossy)
- confluence to confluence (parse and write; lossless and lossy test).
"""
import sys

import dotmpe.du.ext.writer

import init
from util import mkclassname, new_writer_testcase


def create_parser_test(files):
    """
    Test confluence reading/parser.

    - Parse confluence, and write pxml tree.

    * Compare generated pxml with expected pxml.
    """
    for acw_file, pxml_file in files:
        pass

def create_writer_tests(files):
    """
    Test confluence writer.

    - Parse rST, write pxml and confluence.

    * Re-parse generated confluence, and compare pxml tree for lossy 
      structural test.
    """
    for rst_file in files:
        pass

def create_srcwriter_tests(files):
    """
    Test confluence writer as re-writer.

    - Parse confluence, and write pxml and confluence.

    * Compare generated confluence with source for lossless test.
    * Re-parse generated confluence, and compare pxml tree for lossy test.
    """

    for acw_file, pxml_file in files:
        testcase_name = mkclassname(acw_file)

        # Lossy
        TestCase = new_writer_testcase('confluence', testcase_name, acw_file, True)
        TestCase.__module__ = __name__
        setattr(sys.modules[__name__], testcase_name, TestCase)
  

create_parser_test(init.ACW_DOC)
create_writer_tests(init.ACW_DOC)
create_srcwriter_tests(init.ACW_DOC)

