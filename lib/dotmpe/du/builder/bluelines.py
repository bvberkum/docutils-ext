"""
Builders for Blue Lines.
"""
import logging
import docutils
from docutils import readers
from docutils.transforms import universal, references
from dotmpe.du import builder, util
from dotmpe.du.ext.reader import mpe
from dotmpe.du.ext.transform import generate
from dotmpe.du.ext.extractor import form, reference


class Document(builder.Builder):

    settings_overrides = {
        # overridden by bluelines.server:
        #'template': os.path.join(conf.ROOT, 'du-template.txt'),

        # Insert into doctree
        'breadcrumb': True,
        'generator': True,
        'date': True,

        # Clean doctree some (no effect on HTML output):
        'strip_substitution_definitions': True,
        'strip_anonymous_targets': True,

        # Allow document authors to override builder and source ID
        # allow stripping/leaving of these fields.
        'spec_names': ['builder', 'Id', 
            'strip_spec_name',
            'strip_spec_names'],
        'strip_spec_name': ['builder', 'Id'],
        'strip_spec_names': False,

        # This would be writer specific:

        #'stylesheet_path':'/media/style/default.css',
    }

    extractors = (
        #(reference.Extractor, reference.ReferenceStorage()),
        #(extractors.Contact
        #(extractor.docinfo, extractor.docinfo)
    )

    class Reader(mpe.Reader):
        supported = ('bluelines',)
        def get_transforms(self):
            return mpe.Reader.get_transforms(self)


def builder_module_name(node):
    logging.info('TODO: %s', node)
    return node.astext()

def alias_user_reference(node):
    logging.info('TODO: %s', node)
    return node.astext()

AliasApplicationForm = form.FormExtractor
AliasApplicationForm.options_spec = {
        'owner': (alias_user_reference,),
        'build': (builder_module_name,),
        'default-title': (util.du_str,),
        'append-title': (util.yesno,),
        'prepend-title': (util.yesno,),
        'title-separator': (util.du_str,),
        'default-home': (util.du_str,),
        'default-leaf': (util.du_str,),
        'public': (util.yesno,),
    }

def validate_alias_application_form(frmextr, settings):
    return settings

AliasApplicationForm.validate = validate_alias_application_form

class AliasApplication(Document):

    form_store = form.FormStorage()

    extractors = (
            ( AliasApplicationForm, form_store ),
        )


