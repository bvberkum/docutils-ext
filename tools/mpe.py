#!/usr/bin/env python
"""
A minimal front end to the Docutils Publisher with .mpe extensions, 
"""
import os
import sys
try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline

import dotmpe.du.ext 
import dotmpe.docinfo



description = ('')

tool, _names = sys.argv[0], []
tool = tool.split(os.sep).pop()

if '-' in tool:
    _names = tool.split('-')

reader_name = 'mpe'    
if _names:
    if 'mpe' not in _names[0]:
        reader_name = _names.pop(0)
    else:
        _names.pop(0)

if _names:
    writer_name = reader_name+_names.pop(0)
else:
    writer_name = reader_name+'html'

#print >>sys.stderr, reader_name,writer_name
publish_cmdline(
        reader_name=reader_name, 
        writer_name=writer_name, 
        description=description)



#
