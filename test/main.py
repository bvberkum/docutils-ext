"""dotmpe docutils extensions test scripts

Usage (see pydoc unittest.main)
    | python test/main.py [module[.testcase[.test]]]

Ie.
    | python test/main.py rstwriter


Each module is loaded, and create_tests() called if present.
And subsequently unittest.main() started.

XXX: modules are in test/main.list. Can add options here and do away/clean make
   file.. maybe.
"""
import os, re, unittest
import sys

import init
import util
import rstwriter_util


def main(test_modules=[]):

    """
    Run unnitest after loading selected test modules.
    """

    for name in test_modules:
        if '.' in name:
            name = name.split('.')[0]
        m = __import__(name, locals(), globals())
        if hasattr(m, 'create_tests'):
            m.create_tests()
        print >>sys.stderr, "Loaded testmodule '%s'" % name
        setattr(sys.modules[__name__], name, m)

    unittest.main()


if __name__ == '__main__':
    test_modules = sys.argv[1:]
    if test_modules:
        main(test_modules)
    else:
        print >>sys.stderr, "Must pass test modules to load"
        sys.exit(1)
