"""dotmpe docutils extensions test scripts

Usage (see pydoc unittest.main)
    | python test/main.py [module[.testcase[.test]]]

Ie.
    | python test/main.py rstwriter.Test14_LineBlock2
"""
import os, re, unittest
import sys

import init
import util
import rstwriter_util


def main(test_modules=[]):

    """
    Run all tests.
    """

    for name in test_modules:
        m = __import__(name, locals(), globals())
        if hasattr(m, 'create_tests'):
            m.create_tests()
        setattr(sys.modules[__name__], name, m)

    unittest.main()


if __name__ == '__main__': 
    test_modules = sys.argv[1:]
    if test_modules:
        main(test_modules)

