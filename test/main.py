import unittest



def gather_unittests():

    """
    Gather all unittests into one suite.
    """

    import du_test

    tests = []
    for testcase in (
                du_test.RstWriter,
            ):
        tests.append(unittest.TestLoader().loadTestsFromTestCase(testcase))

    #from unit.Document import testcases as Doc_testcases
    #tests += Doc_testcases #+ SGML_testcases

    return tests


def main():

    """
    Run all tests.
    """

    testsuite = unittest.TestSuite(
            gather_unittests() )
    unittest.TextTestRunner(verbosity=2).run(testsuite)


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


