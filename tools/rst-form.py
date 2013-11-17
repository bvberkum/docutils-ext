#!/usr/bin/env python
"""
A front-end to a toy Form reader. Convenient to test various field settings with
`--form-field`.

Does also extract to CSV format. 
FIXME: does not parse command-line options.

Copyleft 2010  Berend van Berkum <dev@dotmpe.com>
This file has been placed in the Public Domain.
"""
import sys, os
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__),
    '..', 'lib')))
from dotmpe.du import form
from dotmpe.du.ext.transform import form1
from dotmpe.du.ext.reader import mpe
from dotmpe.du.ext.writer import htmlform

from docutils import io, readers, Component
from docutils.readers import standalone

# FIXME: uses test form reader with static spec for testing
from test.form import FormReader


#class FormReader(standalone.Reader):
#
#    settings_spec = (
#        'Form Reader', None,
#        form.FormProcessor.settings_spec
#        #+ mpe.Reader.settings_spec[2]
#    )
#
#    def get_transforms(self):
#        return standalone.Reader.get_transforms(self) + [
#        #return readers.Reader.get_transforms(self) + [
#        #return mpe.Reader.get_transforms(self) + [
#            form1.DuForm
#        ]


try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from dotmpe.du.frontend import cli_du_publisher

cli_du_publisher(
        reader_name='mpe',
        parser_name='',
        writer_name=''
    )

from docutils.core import publish_cmdline, default_description,\
    publish_doctree,\
        Publisher
from dotmpe.du.ext.writer.formresults import Writer as FormResultsWriter


#publish_cmdline(reader=FormReader(), writer_name='pseudoxml')#writer=xhtmlform.Writer())

source_path  = sys.argv[1]
source = open(source_path)
#doctree = publish_doctree(source, reader=FormReader())#, writer_name='pseudoxml')
#print doctree

pub = Publisher(FormReader(), 
        writer=FormResultsWriter(),
        source_class=io.FileInput,
        destination_class=io.StringOutput)#, parser, writer, settings=settings,
#                source_class=source_class,
#                destination_class=destination_class)
pub.set_components(None, 'rst', 'pseudoxml')
pub.process_programmatic_settings(None, None, None)
#    settings_spec, settings_overrides, config_section)
pub.set_source(source, source_path)
pub.set_destination(None, None)#destination, destination_path)
output = pub.publish(enable_exit_status=False)

#print pub.document.form_processor.fields
#print pub.document.form_processor.messages
#print pub.document.form_processor.values
print output

