#!/usr/bin/env python
"""
A simple front end for ``dotmpe.du`` `Builder` configurations, for both 
document Du/reST rendering and processing.

Usage::

  rst2<format>-<tag> [docutils publishing options]
  rst-<tag>-proc [docutils processing options]

The 'tag' influences which reader will be used, defaults to 'mpe', so you may
leave this part out. The output format defaults to 'psuedoxml' which will need 
to be set to something like 'latex' or 'html'.

More genericly::

  [<source-format>2<target-format>-][<action>][-<tag>] [options]

where tag may be 'mpe' or another extension (it is the prefix of the reader
name, e.g. 'mpehtml'). Action defaults to 'pub', but may also be 'proc'. It 
does not make sense to have a target-format for a document processing 
invocation though.

At least target-format or tag must be used in the script name.
"""
import os
import sys

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
    locale.setlocale(locale.LC_CTYPE, '')
except:
    pass

from dotmpe.du import frontend
import dotmpe.du.ext # register extensions


description = ('')
actions = ('proc','pub','render')

script_names = os.path.basename(sys.argv[0]).split('-')

# defaults
builder_name = 'mpe'
source_format = 'rst'
target_format = 'pseudoxml'
action = 'pub'

if '2' in script_names[0]:
    source_format, target_format = script_names.pop(0).split('2')
elif script_names[0] in actions:
    action = script_names.pop(0)
else:
    target_format = script_names.pop(0)
if script_names:
    builder_name = script_names.pop(0)
if script_names:
    action = script_names.pop(0)

if '-v' in sys.argv or '--verbose' in sys.argv:
    print >>sys.stderr, """source_format: %s
target_format: %s
builder_name: %s
action: %s""" % (source_format, target_format, builder_name, action)

# Main
if action == 'proc':
    frontend.cli_process(sys.argv[1:], 'dotmpe.du.builder.'+builder_name)

elif action == 'pub':
    # FIXME: reader_name = builder_name + source_format
    writer_name = builder_name+target_format
    frontend.cli_du_publisher(
            reader_name=builder_name, 
            writer_name=writer_name, 
            description=description)

#
