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


script_names = [sys.argv[0]]#os.path.basename(sys.argv[0]).split('-')

if '2' in script_names[0]:
    source_format, target_format = script_names.pop(0).split('2')

reader_name = 'standalone'
if source_format == 'mime':
    parser = comp.get_parser_class('rst')(rfc2822=1)
else:
    parser = comp.get_parser_class(source_format)()
writer_name = target_format

frontend.cli_du_publisher(
        reader_name=reader_name,
        parser=parser,
        writer_name=writer_name)

