"""
"""

import os.path

from dotmpe.du import builder
from dotmpe.du.ext.reader import mpe
from dotmpe.du.ext.extractor import htdocs, reference
from dotmpe.du.util import addClass


class Builder(builder.Builder):

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

            htdocs.Extractor.settings_spec[2] +
            reference.Extractor.settings_spec[2] 
        )

    #  extractor storages
    store_params = {
            'dotmpe.du.ext.extractor.htdocs.HtdocsStorage': ((),
                {'dbref':'sqlite:///.cllct/HtdocsStorage.sqlite'}),
            'dotmpe.du.ext.extractor.reference.ReferenceStorage': ((),
                {'dbref':'sqlite:///.cllct/ReferenceStorage.sqlite'}),
        }

    class Reader(mpe.Reader):

        add_class = [
                'document[0]/section[0],htdocs'
            ]

        def get_transforms(self):
            return mpe.Reader.get_transforms(self) + [
                    addClass(Builder.Reader.add_class) ]


