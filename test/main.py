import unittest

import init


def gather_unittests():

    """
    Gather all unittests into one suite.
    """

    import rstwriter

    tests = []
    for testcase in (
            ):
        tests.append(unittest.TestLoader().loadTestsFromTestCase(testcase))

    for rst_file in init.TEST_DOC:

        testcase = rstwriter.LossyRstWriterTest()
        testcase.RST_FILE = rst_file
        if rst_file.endswith('demo.rst'):
            testcase.corrupt_sources = [rst_file]
        tests.append(testcase)
        #tests.append(unittest.TestLoader().loadTestsFromTestCase(testcase))

        #testcase = rstwriter.LosslessRstWriterTest
        #testcase.RST_FILE = rst_file
        #tests.append(unittest.TestLoader().loadTestsFromTestCase(testcase))


    #from unit.Document import testcases as Doc_testcases
    #tests += Doc_testcases #+ SGML_testcases

    return tests


def main():

    """
    Run all tests.
    """

    testsuite = unittest.TestSuite(
            gather_unittests() )
    unittest.TextTestRunner(verbosity=1).run(testsuite)


if __name__ == '__main__': 
    import sys
    if sys.argv[1:]:
        if sys.argv[1]=='scroll':
            scrolltest_main()
        elif sys.argv[1]=='unit':
            unittest_main()
        else:
            main()
    else:
        main()


