"""
simplemuxdem an experiment with lossless 
text-to-text format based on docutils.

The general idea is that parsing and serializing without "data" loss
is that human produced documents can be updated. This enables all kinds of stuff
restructuring and reformatting, adding metadata, updating references etc.

With lossless text-to-text is meant the ability to reproduce
the exact document while running it thourgh the Du publisher.
The sandbox rst writer has the same philosophy, and saw it required to customize
the parser with this in mind: some document elements would need to remember
where there was extra whitespace.
This means losslessness is always lost with inter-format conversions.

But regarding the actual information, the data captured is less than in the
original document. This "common" document tree is easily compared using
output from the psuedo-xml writer.

simplemuxdem uses a parser 'simplereader' that is based on the rSt parser,
and there is no writer yet. 
"""
import sys

import dotmpe.du.ext.parser

import init
from util import mkclassname, new_parser_testcase


def create_tests(files):

    for smf_file, pxml_file in files:
        testcase_name = mkclassname(smf_file)

        # Lossy - compare to PXML
        TestCase = new_parser_testcase('simplereader', testcase_name, smf_file,
                pxml_file, True)
        TestCase.__module__ = __name__
        setattr(sys.modules[__name__], testcase_name, TestCase)
        # Need writer for lossless compare
  

create_tests(init.SMF_DOC)

