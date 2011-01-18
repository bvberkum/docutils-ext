#!/usr/bin/env python
"""
A minimal front end for builder configurations.
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
#import mkdocs


description = ('')
actions = ('proc','pub','render')

tool = os.path.basename(sys.argv[0])
if '-' in tool:
    _names = tool.split('-')
else:
    _names = [tool]

if len(_names) == 1 or _names[1] not in actions:
    _names.insert(1, 'pub')

builder_name = _names.pop(0)
action = _names.pop(0)
#print >>sys.stderr, builder_name, action

if action == 'proc':
    #print >>sys.stderr, 'proc', builder_name
    frontend.cli_process('dotmpe.du.builder.'+builder_name)

elif action == 'pub':
    if _names:
        writer_name = builder_name+_names.pop(0)
        #writer_name = _names.pop(0)
    else:
        writer_name = builder_name+'html'

    #print >>sys.stderr, builder_name,writer_name
    frontend.cli_du_publisher(
            reader_name=builder_name, 
            writer_name=writer_name, 
            description=description)

#
