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


class DuFrontend(object):

    def run(self):
        pass


#name = sys.argv[0]
#if os.sep in name:
#    name = os.path.basename(name)
#script_names = [name]
#
#assert '2' in name
#source_format, target_format = name.split('2')
#
#reader_name = 'standalone'
#if source_format == 'mime':
#    parser = comp.get_parser_class('rst')(rfc2822=1)
#else:
#    parser = comp.get_parser_class(source_format)()
#writer_name = target_format

reader_name = 'standalone-mpe'
parser = comp.get_parser_class('rst')()
writer_name = 'rst'#pprint'

print 'Reader:', reader_name,
print 'Parser:', parser,
print 'Writer:', writer_name

frontend.cli_du_publisher(
        reader_name=reader_name,
        parser=parser,
        writer_name=writer_name)

