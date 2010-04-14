"""
Standalone builder.
"""
from dotmpe.du import builder
from dotmpe.du.ext.reader import mpe


class Document(builder.Builder):

    settings_overrides = {
        'stylesheet_path':'/media/style/default.css',
#            'template': os.path.join(conf.ROOT, 'du-template.txt'),
        'strip_substitution_definitions': True,
        'strip_anonymous_targets': True,
        'spec_names': ['cc-license','generator','timestamp','source-link'],
        'strip_spec_names': ['cc-license','generator','timestamp','source-link'],
    }

    Reader = mpe.Reader


