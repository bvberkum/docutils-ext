#!/usr/bin/env python
"""
A new script to access the older publisher.

There is no way to access new components yet I think, should look at how aliases
work etc.
"""
import os
import sys

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
    locale.setlocale(locale.LC_CTYPE, '')
except:
    pass

from dotmpe.du import frontend, comp
import dotmpe.du.ext # register extensions


name = sys.argv[0]
if os.sep in name:
    name = os.path.basename(name)

reader_name = 'standalone-mpe'

if '2' in name:
    source_format, target_format = name.split('2')
    writer_name = target_format
else:
    writer_name = 'pseudoxml'

parser = comp.get_parser_class('rst')()

if '--debug-du-fe' in sys.argv:
    sys.argv.remove('--debug-du-fe')


frontend.cli_du_publisher(
        reader_name=reader_name,
        parser=parser,
        writer_name=writer_name)
