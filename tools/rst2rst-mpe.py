#!/usr/bin/env python
"""
A new script to access the older publisher with sandbox rst writer.
"""
import os
import sys
from os.path import dirname

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
    locale.setlocale(locale.LC_CTYPE, '')
except:
    pass

from docutils.core import publish_cmdline

from dotmpe.du import frontend, comp
import dotmpe.du.ext # register extensions


script_names = [sys.argv[0]]#os.path.basename(sys.argv[0]).split('-')

if '2' in script_names[0]:
    source_format, target_format = script_names.pop(0).split('2')

reader_name='standalone'
parser_name='rst'
# XXX: this work because docutils was monkeypatched by dotmpe.du.ext:
writer_name='rst-mpe'

publish_cmdline(
        parser_name=parser_name,
        reader_name=reader_name, 
        writer_name=writer_name)



