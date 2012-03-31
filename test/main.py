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
        setattr(sys.modules[__name__], name, __import__(name, locals(), globals()))

    unittest.main()


if __name__ == '__main__': 
    # to run unittest, use testmodule name for argument:
    listing_file = os.environ.get('test_listing')
    assert listing_file
    test_modules = filter(lambda x:not x.startswith('#'),
            filter(len,
                map(lambda x:x.strip(),
                    open(listing_file).readlines())))
    main(test_modules)

