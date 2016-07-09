#!/usr/bin/env python
import os
import sys

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
    locale.setlocale(locale.LC_CTYPE, '')
except:
    pass

from dotmpe.du import frontend, comp


reader_name = 'standalone-mpe'
parser = comp.get_parser_class('rst')()
writer = comp.get_writer_class('outline')()

frontend.cli_du_publisher(
        reader_name=reader_name,
        parser=parser,
        writer=writer)

