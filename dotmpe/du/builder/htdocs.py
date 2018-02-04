"""
"""

import os.path

from dotmpe.du import builder, util
from dotmpe.du.ext.reader import standalone
from dotmpe.du.ext.extractor import htdocs, reference, docinfo


class Builder(builder.Builder):

    HTSTORE = 'sqlite:///%s' % os.path.expanduser('~/.cllct/htdocs.sqlite')

    settings_default_overrides = {
        'file_insertion_enabled': 'include',
        'halt_level': 3,
        'report_level': 6
    }

    extractor_spec = [
            ('dotmpe.du.ext.extractor.docinfo', ),
            ('dotmpe.du.ext.extractor.htdocs', ),
            ('dotmpe.du.ext.extractor.reference', ),
#              ('dotmpe.du.ext.extractor.logbook', ), # see dotmpe builder
        ]

    settings_spec = (
                'htdocs.mpe Builder',
                'Metadata extractor, cross reference, and inline expand. ' +
                reference.Extractor.settings_spec[1],
            ((
                 'Taxus DB reference. ',
                 ['--dbref'],
                 {
                     'metavar': 'PATH',
                     'default': HTSTORE
                     #'validator': util.optparse_init_sqlalchemy,
                 }
            ),) +
            docinfo.Extractor.settings_spec[2] +
            htdocs.Extractor.settings_spec[2] +
            reference.Extractor.settings_spec[2]
        )

    #  extractor storages
    store_params = {

#            'dotmpe.du.ext.extractor.htdocs.HtdocsStorage': ((),
#                {'dbref': HTSTORE}),

#            'dotmpe.du.ext.extractor.reference.ReferenceStorage': ((),
#                {'dbref': HTSTORE}),
        }

    class Reader(standalone.Reader):

        add_class = [
                'document[0]/section[0],htdocs'
            ]

        def get_transforms(self):
            return standalone.Reader.get_transforms(self) + [
                    util.addClass(Builder.Reader.add_class) ]
