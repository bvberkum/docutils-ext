#!/usr/bin/env python
"""
A minimal front end to the Docutils Publisher, producing HTML.

Copyleft 2009  Berend van Berkum <dev@dotmpe.com>
This file has been placed in the Public Domain.
"""
import dotmpe.du.ext
from dotmpe.du.ext.writer import xhtml, rst

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, default_description


description = ('Generates (X)HTML documents from standalone reStructuredText '
               'sources.  ' + default_description)

#publish_cmdline(writer_name='dotmpe-htdocs', description=description)
#publish_cmdline(writer=xhtml.Writer(), description=description)
publish_cmdline(writer=rst.Writer(), description=description)

