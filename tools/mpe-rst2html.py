#!/usr/bin/env python

"""
A minimal front end to the Docutils Publisher with .mpe extensions, 
html output.
"""

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline
import dotmpe.du.ext 

description = ('')

publish_cmdline(reader_name='mpe', writer_name='mpehtml', description=description)



