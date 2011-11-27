"""
dotmpe.com v5 writer

This is an aggregation and configuration of Du components.
"""
from dotmpe.du import builder, util
from dotmpe.du.ext.transform import include
from dotmpe.du.ext.reader import mpe
from dotmpe.du.util import addClass


class Builder(builder.Builder):

    settings_default_overrides = {
        '_disable_config': True,
        'stylesheet_path':'/media/style/default.css',
        'script': 'http://ajax.googleapis.com/ajax/libs/jquery/1.4.1/jquery.min.js,/media/script/default.js',
        'embed_stylesheet': False,
        'embed_script': False,
        'breadcrumb': True,
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
    }

    # TODO: integrate with CLI/settings_spec
    extractor_spec = [
            ('nabu.extractors.document', ),
            ('dotmpe.du.ext.extractor.settings', 'dotmpe.du.extractor.SettingsStorage')
        ] 

    store_params = {
            'nabu.extractors.document': ((),{}),
        }

    class Reader(mpe.Reader):

        add_class = [
                'document[0]/section[0],dotmpe-v5'
            ]

        def get_transforms(self):
            return mpe.Reader.get_transforms(self) + [
                addClass(Builder.Reader.add_class) ]

    class ReReader(builder.Builder.ReReader):
        settings_spec = (
            'Blue Lines doctree (re)reader. ',
            None, (),)
        def get_transforms(self):
            return builder.Builder.ReReader.get_transforms(self) + [
                debug.Settings,                 # 500
                debug.Options,                  # 500
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
                addClass(Page.Reader.add_class) ]


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


