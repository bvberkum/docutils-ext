"""
"""
__docformat__ = 'reStructuredText'

import re

from optparse import Values

from docutils import writers, nodes, frontend
from docutils.transforms import writer_aux



class Writer(writers.Writer):

    """
    Write values to CSV.
    """

    defaults = Values(dict(
        output_format = 'csv',
        denormalize_lists = True,
        concat_lists = False,
        field_delimiter = ',',
        auto_quote = False
    ))
    "Place to set static default values for all options. "

    settings_spec = (
            'Form results writer',
            None,
            ((
                "Output format",
                ['--form-results-format'],
                { 'default': defaults.output_format, 'metavar': '<FORMAT>' }),
            (
                "Field delimiter. ",
                ['--form-results-delimiter'],
                { 'default': defaults.field_delimiter, 'metavar': '<DELIM>' }),
            (
                "Automatically quote fiels. ",
                ['--form-results-auto-quote'],
                { 'default': defaults.auto_quote,
                    'action': defaults.auto_quote and 'store_false' or 'store_true' }),
            (
                "For list values, output a row for each value. "
                "",
                ['--form-denormalize-lists'],
                { 'default': defaults.denormalize_lists, 'action':
                    defaults.denormalize_lists and 'store_false' or 'store_true' }),
            (
                "For list values, concatenate. "
                "",
                ['--form-append-lists'],
                { 'default': defaults.concat_lists, 'action':
                    defaults.concat_lists and 'store_false' or 'store_true' }),
            ))

    def get_transforms(self):
        return writers.Writer.get_transforms(self) + [
            #writer_aux.Admonitions
                ]

    def __init__(self):
        writers.Writer.__init__(self)

    def init_from_settings(self):
        settings = self.document.settings
#        self.output_format = getattr(settings, 'form_result_format',
#                self.__class__.defaults.result_format)
        self.concat_lists = getattr(settings, 'form_append_lists',
                self.__class__.defaults.concat_lists)
        self.denormalize_lists = getattr(settings, 'form_denormalize_lists',
                self.__class__.defaults.denormalize_lists)
        self.delimiter = getattr(settings, 'form_results_delimiter',
                self.__class__.defaults.field_delimiter)
        self.auto_quote = True

    def translate(self):
        self.init_from_settings()
        self.lines = []
        formproc = self.document.form_processor
        for field_id in formproc:
            field = formproc.fields[field_id]
            self.write_field(field)
        self.output = "\n".join(self.lines)

    def write_field(self, field):
        formproc = self.document.form_processor
        delimited_fields = [ field.field_id ]
        val = formproc[field.field_id]
        if field.append and self.denormalize_lists:
            self.nested_write(delimited_fields, val)
            return
        if self.concat_lists and isinstance(val, list):
            delimited_fields += val
        else:
            delimited_fields.append(val)
        self.write_delimited(*delimited_fields)

    def nested_write(self, path, values):
        path = list(path)
        for i, val in enumerate(values):
            fields = list(path)
            fields.append( "_%s" % i )
            if isinstance(val, list):
                self.nested_write( fields, val )
            else:
                fields.append(val)
                self.write_delimited(*fields)

    def write_delimited(self, *fields):
        line = []
        for f in fields:
            if self.auto_quote and isinstance(f, basestring):
                if re.search('\s', f):
                    f = repr(f) # unicode
            if not f:
                f = ''
            if not isinstance(f, basestring):
                f = str(f)
            line.append(f)
        self.lines.append(self.delimiter.join(line))

