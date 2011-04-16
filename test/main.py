"""dotmpe docutils extensions test scripts

Usage (see pydoc unittest.main)
    | python test/main.py [module[.testcase[.test]]]

Ie.
    | python test/main.py rstwriter.Test14_LineBlock2
"""
import os, re, unittest

import init
import rstwriter



def main():

    """
    Run all tests.
    """
   
    rstwriter.create_tests(init.TEST_DOC)
    # XXX:BVB: fixme: Form

    unittest.main()


if __name__ == '__main__': 
    import sys
    main()


