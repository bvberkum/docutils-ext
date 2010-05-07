#!/usr/bin/python
"""
A minimal front end to the Docutils Publisher, producing Docutils XML.

This demonstrates rSt's 'email' reader. It does assume however that not only the
message contents but also its headers contain rSt compatible text, so this is not
entirely useful on just any email messge.

Copyleft 2009  Berend van Berkum <dev@dotmpe.com>
This file has been placed in the Public Domain.
"""

import sys, os
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__),
    '..', 'lib')))
import dotmpe.du.ext
from dotmpe.du import comp
from dotmpe.du.ext.reader import mpe

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, default_description

parser = comp.get_parser_class('rst')(rfc2822=1)
publish_cmdline(reader=comp.get_reader_class('standalone')(), 
        parser=parser,
        writer_name='pseudoxml')


