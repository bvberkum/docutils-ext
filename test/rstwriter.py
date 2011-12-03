import sys

import init
from util import mkclassname, new_writer_testcase



def create_tests(files):

    for rst_file in files:
        testcase_name = mkclassname(rst_file)

        # Lossy
        TestCase = new_writer_testcase('rst-mpe', testcase_name, rst_file, True)
        if rst_file.endswith('demo.rst'):
            TestCase.corrupt_sources = [rst_file]
        setattr(sys.modules[__name__], testcase_name, TestCase)

        # Lossless

# XXX:BVB: reinstate lossless tests
        #TestCase = new_rstwriter_testcase(testcase_name, rst_file, False)
        #if rst_file.endswith('demo.rst'):
        #    TestCase.corrupt_sources = [rst_file]
        #setattr(sys.modules[__name__], testcase_name, TestCase)


create_tests(init.RST_DOC)

