#!/usr/bin/env python
"""
A minimal front end to the Docutils Publisher with mkdoc extensions and storage.
"""
import os
import sys
try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline

from dotmpe.du import frontend
import dotmpe.du.ext # register extensions
import mkdoc


description = ('')
actions = ('proc','pub')

tool = os.path.basename(sys.argv[0]), 
if '-' in tool:
    _names = tool.split('-')
else:
    _names = [tool]

if len(_names) == 1 or _names[1] not in actions:
    _names.insert(1, 'pub')

reader_name = _names.pop(0)
action = _names.pop(0)


if action == 'proc':
    frontend.cli_process('')

elif action == 'pub':
    if _names:
        writer_name = reader_name+_names.pop(0)
    else:
        writer_name = reader_name+'html'

    #print >>sys.stderr, reader_name,writer_name
    frontend.cli_publisher(
            reader_name=reader_name, 
            writer_name=writer_name, 
            description=description)

#
