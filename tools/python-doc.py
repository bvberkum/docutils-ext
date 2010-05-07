#!/usr/bin/python
"""
A minimal front end to the Docutils Publisher, producing Docutils XML.
This uses the (experimental?) Python source reader. 
TODO: there is no HTML writer compatible with it afaik

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

publish_cmdline(
        reader=comp.get_reader_class('python')(), 
        writer=comp.get_writer_class('dotmpe-html')())


