"""
See ReadMe 'testing' section for some docs.
"""

import sys

import init
from util import mkclassname, new_writer_testcase



def create_lossy_pxml_compare_tests(tag, files):

    for rst_file in files:
        testcase_name = mkclassname(rst_file)

        # Lossy

        TestCase = new_writer_testcase(tag, testcase_name, rst_file, True)
        setattr(sys.modules[__name__], testcase_name, TestCase)


def create_lossess_compare_tests(tag, files):

    for rst_file in files:
        testcase_name = mkclassname(rst_file)

        # Lossless

        TestCase = new_writer_testcase(tag, testcase_name, rst_file, False)
        setattr(sys.modules[__name__], testcase_name, TestCase)


def create_tests():
    create_lossy_pxml_compare_tests('rst-mpe', init.RST_LOSSY_DOC)
    create_lossess_compare_tests('rst-mpe', init.RST_LOSSLESS_DOC)

