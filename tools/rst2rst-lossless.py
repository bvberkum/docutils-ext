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

sys.path.insert(0, os.path.join(dirname(dirname(__file__)), 'lib', 'docutils-branches',
	'lossless-rst-writer', 'docutils', 'writers'))
# XXX: access extension module directly
try:
    LOSSLESS_WRITER = __import__('rst') 
except ImportError, e:
    print "rst2rst-lossless: Cannot find lossless-rst-writer:", e
    sys.exit(1)

reader_name='standalone'
parser_name='rst'
writer_class=LOSSLESS_WRITER.Writer
writer_name='rst-lossless'

publish_cmdline(
#        parser=parser, 
        parser_name=parser_name,
#        reader=reader_class(parser), 
        reader_name=reader_name, 
        writer=writer_class(), 
        writer_name=writer_name)

