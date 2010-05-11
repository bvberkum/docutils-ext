#!/usr/bin/env python
"""
A front-end to a toy Form reader. Convenient to test various field settings with
`--form-field`.

Copyleft 2010  Berend van Berkum <dev@dotmpe.com>
This file has been placed in the Public Domain.
"""
import sys, os
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__),
    '..', 'lib')))
from dotmpe.du import form
from dotmpe.du.ext.transform import form1
from dotmpe.du.ext.reader import mpe
from dotmpe.du.ext.writer import xhtmlform


class FormReader(mpe.Reader):

    settings_spec = (
        'Form Reader', None,
        form.FormProcessor.settings_spec
        #+ mpe.Reader.settings_spec[2]
    )

    def get_transforms(self):
        from docutils import readers, Component
        return readers.Reader.get_transforms(self) + [
        #return mpe.Reader.get_transforms(self) + [
            form1.DuForm
                ]


try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, default_description
publish_cmdline(reader=FormReader(), writer_name='pseudoxml')#writer=xhtmlform.Writer())

