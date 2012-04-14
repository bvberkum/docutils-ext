"""
Writer tests for Atlassian Confluence documents
(atlassian confluence wiki format).

- rST to confluence (write; lossy)
"""
import sys

import dotmpe.du.ext.writer

import init
from util import mkclassname, new_writer_testcase


def create_writer_tests(files):
    """
    Test confluence writer.

    - Parse rST, write pxml and confluence.

    * Re-parse generated confluence, and compare pxml tree for lossy 
      structural test.
    """
    for rst_file, pxml_file in files:

        testcase_name = mkclassname(rst_file)

        # Lossy
        TestCase = new_writer_testcase('confluence-embedded',
                testcase_name, rst_file, True)
        TestCase.__module__ = __name__
        setattr(sys.modules[__name__], testcase_name, TestCase)


create_writer_tests(init.ACW_DOC)

