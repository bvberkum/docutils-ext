"""
dotmpe.com v5 writer
"""
from dotmpe.du import builder
from dotmpe.du.ext.transform import include
from dotmpe.du.ext.reader import mpe
from dotmpe.du.util import addClass


class Builder(builder.Builder):

    settings_overrides = {
            'stylesheet_path':'/media/style/default.css',
            'javascript_paths': [],
            'breadcrumb': True,
            'generator': False,
            'date': True,
            'input_encoding': 'utf-8',
            'output_encoding': 'utf-8',
            'spec_names': ['cc-license','generator','timestamp'],
            'strip_spec_names': ['edition','class'],
            'file_insertion_enabled': False,
            #'raw_enabled': False,
            'cc_license': 'by nc sa',
            'cc_embed': True,
            # cleanup nice for tree-output, not needed for XHTML writer
            'strip_substitution_definitions': True,
            'strip_anonymous_targets': True,
        }

    class Reader(mpe.Reader):

        add_class = [
                'document[0]/section[0],dotmpe-v5'
            ]

        def get_transforms(self):
            return mpe.Reader.get_transforms(self) + [
                addClass(Builder.Reader.add_class) ]


class Page(Builder):

    settings_overrides = {
            'cc-license': 'by-nd'
        }

    class Reader(Reader):

        add_class = Reader.add_class + [
                'document[0]/section[0],page',
            ]

        def get_transforms(self):
            return mpe.Reader.get_transforms(self) + [
                addClass(Page.Reader.add_class) ]


class Frontpage(Page):

    settings_overrides = {
            'javascript_paths': [
                'http://ajax.googleapis.com/ajax/libs/jquery/1.4.1/jquery.min.js',
                '/media/script/frontpage.js',
            ]
        }

    class Reader(Page):

        add_class = Reader.add_class + [
                'document[0]/section[0],frontpage',
            ]

        def get_transforms(self):
            return mpe.Reader.get_transforms(self) + [
                addClass(Frontpage.Reader.add_class) ]


