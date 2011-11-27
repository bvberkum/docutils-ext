#!/usr/bin/env python
"""
A minimal front end to the Docutils Publisher, producing man-page files.

Copyleft 2009  Berend van Berkum <dev@dotmpe.com>
This file has been placed in the Public Domain.
"""
import sys, os
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__),
    '..', 'lib')))
from dotmpe.du.ext.reader import mpe
from docutils.writers import manpage

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, default_description


description = ('Generates man-page files from standalone reStructuredText '
               'sources.  ' + default_description)

publish_cmdline(reader=mpe.Reader(), writer=manpage.Writer(), description=description)

