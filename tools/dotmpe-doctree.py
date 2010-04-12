#!/usr/bin/python
"""
A minimal front end to the Docutils Publisher, producing Docutils XML.

Copyleft 2009  Berend van Berkum <dev@dotmpe.com>
This file has been placed in the Public Domain.
"""
import dotmpe.du.ext
from dotmpe.du.ext.reader import mpe

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, default_description


description = ('Generates Docutils-native XML from standalone '
               'reStructuredText sources.  ' + default_description)

publish_cmdline(reader=mpe.Reader(), writer_name='pseudoxml', description=description)
