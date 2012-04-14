"""
Muxdem tests for Atlassian Confluence documents
(atlassian confluence wiki format).

- confluence to confluence (parse and write; lossless and lossy test).
"""
import sys

import dotmpe.du.ext.writer

import init
from util import mkclassname, new_writer_testcase


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
        TestCase = new_writer_testcase('confluence-embedded', 
                testcase_name, acw_file, True)
        print TestCase
        TestCase.__module__ = __name__
        setattr(sys.modules[__name__], testcase_name, TestCase)
 

create_srcwriter_tests(init.ACW_DOC)


