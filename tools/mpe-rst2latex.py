#!/usr/bin/env python

"""
A minimal front end to the Docutils Publisher with .mpe extensions, producing LaTeX.
"""

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline
import dotmpe.du.ext 

description = ('Generates LaTeX documents from standalone reStructuredText '
               'sources. '
               'Reads from <source> (default is stdin) and writes to '
               '<destination> (default is stdout).  See '
               'dotmpe.com/project/docutils.mpe or'
               '<http://docutils.sourceforge.net/docs/user/latex.html> for '
               'the full reference.')

publish_cmdline(reader_name='mpe', writer_name='mpelatex', description=description)

