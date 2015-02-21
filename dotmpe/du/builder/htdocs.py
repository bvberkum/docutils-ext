"""
"""

import os.path

from dotmpe.du import builder, util
from dotmpe.du.ext.reader import mpe
from dotmpe.du.ext.extractor import htdocs, reference


class Builder(builder.Builder):

    HTSTORE = 'sqlite:///.cllct/HtdocsStorage.sqlite'

    settings_defaults_overrides = {
            }

    extractor_spec = [
            ('dotmpe.du.ext.extractor.htdocs', ),
            ('dotmpe.du.ext.extractor.reference', ),
#              ('dotmpe.du.ext.extractor.logbook', ), # see dotmpe builder
        ]

    settings_spec = (
            'htdocs.mpe Builder',
            '. ',
            ((
                 'Database to store titles. ',
                 ['--dbref'],
                 {
                     'metavar':'PATH', 
                     'default': HTSTORE
                     #'validator': util.optparse_init_sqlalchemy,
                 }
            ),) +
            reference.Extractor.settings_spec[2] 
        )

    #  extractor storages
    store_params = {

            'dotmpe.du.ext.extractor.htdocs.HtdocsStorage': ((),
                {'dbref':HTSTORE}),

            'dotmpe.du.ext.extractor.reference.ReferenceStorage': ((),
                {'dbref':'sqlite:///.cllct/ReferenceStorage.sqlite'}),
        }

    class Reader(mpe.Reader):

        add_class = [
                'document[0]/section[0],htdocs'
            ]

        def get_transforms(self):
            return mpe.Reader.get_transforms(self) + [
                    util.addClass(Builder.Reader.add_class) ]


