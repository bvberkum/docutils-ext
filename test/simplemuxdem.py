"""
Test parsing of simple-muxdem formatting.
"""
import sys

import dotmpe.du.ext.parser

import init
from util import mkclassname, new_parser_testcase


def create_lossy_pxml_compare_tests(files):

    for smf_file, pxml_file in files:
        testcase_name = mkclassname(smf_file)

        # Lossy
        TestCase = new_parser_testcase('simplereader', testcase_name, smf_file,
                pxml_file, True)
        TestCase.__module__ = __name__
        setattr(sys.modules[__name__], testcase_name, TestCase)
  

def create_tests():
    create_lossy_pxml_compare_tests(init.SMF_DOC)

