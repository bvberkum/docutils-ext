#!/usr/bin/env python
"""
Publisher for W&S documentation,
based on the Python Docutils publisher.

Use as::

    script-name-{output-format}[.ext]

ie.::

    ws-crm-xhtml
    ws-docs-pdf.py

For arguments see Docutils options in ``--help``.
"""
import os
import sys
try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

import docutils
from docutils import io
from docutils.core import Publisher, publish_cmdline
from docutils.readers import doctree

#import dotmpe.du.ext # register Du extensions


# Determine output format from executable filename
output_formats = ('pseudoxml', 'brx_ws_html', 'latex', 'html', 'xml') 
# TODO: support pdf here would be nice

tool = os.path.basename(sys.argv[0])
if '.' in tool:
    tool = tool[:tool.find('.')]
if '-' in tool:
    _names = tool.split('-')
else:
    _names = [tool]

output_format = _names.pop()
if output_format == 'pub':
	output_format = 'pseudoxml'
assert output_format in output_formats, "Cannot handle %s ouput" % output_format


### 1. Read main document and preprocess to doctree,
###    apply extraction/rewriter transforms.

# Prepare publisher

usage = "%prog [options] [<source> [<destination>]]"
description = ('Reads main document from standalone reStructuredText '
               'from <source> (default is stdin). ')
#reader_name='mpe_brx_ws'
reader_name = 'standalone'
writer_name = output_format

pub = Publisher(None, None, None, 
    settings=None,
    destination_class=io.NullOutput)

# Get settings for components from command-line
pub.set_components(reader_name, 'rst', writer_name) 
pub.process_command_line(None, None, None, None, {})

# Publish to doctree using reader/parser but without writing
pub.set_components(reader_name, 'rst', 'null') 
null_output = pub.publish(
    None, usage, description, None, None,
    config_section=None, enable_exit_status=1)
document = pub.document


### 2. Render doctree to output format, 
###    apply completion transforms.

pub.reader = doctree.Reader(parser_name='null')
pub.set_writer(output_format)
pub.destination_class = io.FileOutput
pub.set_destination() # reset null-out to file-out

document.settings = pub.settings
pub.source = io.DocTreeInput(document)

pub.apply_transforms()
output = pub.writer.write(pub.document, pub.destination)
pub.writer.assemble_parts()


# ----

