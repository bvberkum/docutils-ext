import os.path

from dotmpe.du import builder
from dotmpe.du.ext.reader import mpe
from dotmpe.du.util import addClass


class Builder(builder.Builder):

    settings_defaults_overrides = {
            }

    extractor_spec = [
            ('dotmpe.du.ext.extractor.htdocs', ),
        ]

    #  xxx: rename to extractor params?
    store_params = {
            'HtdocsStorage': ((),
                {'dbref':'sqlite:///'+os.path.expanduser('~/.cllct/db.sqlite')}),
        }

    class Reader(mpe.Reader):

        add_class = [
                'document[0]/section[0],htdocs'
                ]

        def get_transforms(self):
            return mpe.Reader.get_transforms(self) + [
                    addClass(Builder.Reader.add_class) ]


