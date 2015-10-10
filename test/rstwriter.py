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
        if rst_file.endswith('demo.rst'):
            TestCase.corrupt_sources += [rst_file]
        setattr(sys.modules[__name__], testcase_name, TestCase)


def create_lossess_compare_tests(files):

    for rst_file in files:
        testcase_name = mkclassname(rst_file)

        # Lossless

        TestCase = new_writer_testcase(testcase_name, rst_file, False)
        if rst_file.endswith('demo.rst'):
            TestCase.corrupt_sources += [rst_file]
        if rst_file.endswith('bug.rst'):
            TestCase.corrupt_sources += [rst_file]
        setattr(sys.modules[__name__], testcase_name, TestCase)


def create_tests():
    create_lossy_pxml_compare_tests('rst-mpe', init.RST_DOC)
    # XXX:BVB: reinstate lossless tests
    #create_lossess_compare_tests(init.RST_DOC)

