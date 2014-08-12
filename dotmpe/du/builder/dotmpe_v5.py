"""
dotmpe.com v5 writer

This is an aggregation and configuration of Du components.
"""
from dotmpe.du import builder, util
from dotmpe.du.ext.transform import include, logbook
from dotmpe.du.ext.reader import mpe
from dotmpe.du.util import addClass


def _get_logbook_store(options):
    """Temporary stuff until storage component instances are properly managed.
    """
    import sqlite3
    dbf = options['logbook_db']
    try:
        return sqlite3.connect(dbf)
    except sqlite3.OperationalError:
        raise util.DatabaseConnectionError("Cannot connect to %s" % dbf)


class Builder(builder.Builder):

    settings_default_overrides = {
        '_disable_config': True,
        'stylesheet_path':'/media/style/default.css',
        'script': 'http://ajax.googleapis.com/ajax/libs/jquery/1.4.1/jquery.min.js,/media/script/default.js',
        'embed_stylesheet': False,
        'embed_script': False,
        'breadcrumb': False,#True,
        'generator': False,
        'date': True,
        'input_encoding': 'utf-8',
        'output_encoding': 'utf-8',
        #'file_insertion_enabled': False,
        #'raw_enabled': False,
        'cc_license': 'by nc sa',
        'cc_embed': True,
        # cleanup nice for tree-output, not needed for XHTML writer
        'strip_substitution_definitions': True,
        'strip_anonymous_targets': True,
        'user_settings': [
            'generator','timestamp'
            'build', 'id', 'cc-license', 'strip_setting_names',
        ],
        'strip_settings_names': ['build', 'id', 'cc-license',],
        'strip_user_settings': False,
        'compact_lists': False,
        'compact_field_lists': False,
        'logbook_db': 'var/lib/htdocs/dotmpe-v5-logbook.db'
    }

    # TODO: integrate with CLI/settings_spec
    extractor_spec = [
            ('nabu.extractors.document', 'dotmpe.du.ext.extractor.document'),
            ('dotmpe.du.ext.extractor.settings', 'dotmpe.du.ext.extractor.settings.SettingsStorage')
        ] 

    store_params = {
            'dotmpe.du.ext.extractor.document.Storage': (
                (),
                {'module':None, 'connection': _get_logbook_store}),
        }

    class Reader(mpe.Reader):

        add_class = [
                'document[0]/section[0],dotmpe-v5'
            ]

        def get_transforms(self):
            return mpe.Reader.get_transforms(self) + [
                    addClass(Builder.Reader.add_class),
                    logbook.LogBook
                ]

    class ReReader(builder.Builder.ReReader):
        settings_spec = (
            'Blue Lines doctree (re)reader. ',
            None, (),)
        def get_transforms(self):
            return builder.Builder.ReReader.get_transforms(self) + [
                    debug.Settings,                 # 500
                    debug.Options,                  # 500
                    logbook.LogBook
                ]


class Page(Builder):

    settings_default_overrides = util.merge(
        Builder.settings_default_overrides.copy(), **{
            'cc-license': 'by-nd',
            'script': 'http://ajax.googleapis.com/ajax/libs/jquery/1.4.1/jquery.min.js,/media/script/default.js,/media/script/page.js',
        })

    class Reader(Builder.Reader):

        add_class = Builder.Reader.add_class + [
                'document[0]/section[0],page',
            ]

        def get_transforms(self):
            return mpe.Reader.get_transforms(self) + [
                    addClass(Page.Reader.add_class),
                ]


class Frontpage(Page):

    settings_default_overrides = util.merge(
        Page.settings_default_overrides.copy(), **{
            'script': 'http://ajax.googleapis.com/ajax/libs/jquery/1.4.1/jquery.min.js,/media/script/default.js,/media/script/frontpage.js',
        })

    class Reader(Page.Reader):

        add_class = Page.Reader.add_class + [
                'document[0]/section[0],frontpage',
            ]

        def get_transforms(self):
            return mpe.Reader.get_transforms(self) + [
                addClass(Frontpage.Reader.add_class) ]


