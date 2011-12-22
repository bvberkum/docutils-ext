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
import sys
test_modules = filter(lambda x:not x.startswith('#'),
        filter(len,
            map(lambda x:x.strip(),
                open('test/main.list').readlines())))
for name in test_modules:
    setattr(sys.modules[__name__], name, __import__(name, locals(), globals()))


def main():

    """
    Run all tests.
    """

    unittest.main()


if __name__ == '__main__': 
    import sys
    main()

