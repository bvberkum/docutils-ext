"""dotmpe docutils extensions test scripts

Usage (see pydoc unittest.main)
    | python test/main.py [module[.testcase[.test]]]

Ie.
    | python test/main.py rstwriter.Test14_LineBlock2
"""
import os, re, unittest

import init
import util
import rstwriter_util
# to run unittest, use testmodule name for argument:
import rstwriter
import atlassianwriter
import form


def main():

    """
    Run all tests.
    """

    unittest.main()


if __name__ == '__main__': 
    import sys
    main()

