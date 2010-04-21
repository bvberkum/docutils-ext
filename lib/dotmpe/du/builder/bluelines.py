"""
Builders for Blue Lines.
"""
import logging
import docutils
from docutils import readers
from docutils.transforms import universal, references
from dotmpe.du import builder
from dotmpe.du.ext.reader import mpe
from dotmpe.du.ext.transform import generate
from dotmpe.du.ext.extractor import form, reference


class Document(builder.Builder):

    settings_overrides = {
        # overridden by bluelines.server:
#      'template': os.path.join(conf.ROOT, 'du-template.txt'),
        # Insert into doctree
        'breadcrumb': True,
        'generator': True,
        'date': True,
        # Clean doctree some (no effect on HTML output):
        'strip_substitution_definitions': True,
        'strip_anonymous_targets': True,
        # Allow document authors to override builder and source ID
        'spec_names': ['build', 'Id'],
        'strip_spec_names': ['build', 'Id'],
        # This would be writer specific:
        'stylesheet_path':'/media/style/default.css',
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


def yesno(argument):
    return docutils.parsers.rst.directives.choice(argument, ('yes', 'no'))

def builder_module_name(argument):
    logging.info('TODO: %s', argument)
    return argument

def alias_user_reference(argument):
    logging.info('TODO: %s', argument)
    return argument

AliasApplicationFormExtractor = form.FormExtractor
AliasApplicationFormExtractor.option_spec = {
        'owner': alias_user_reference,
        'builder': builder_module_name,
        'default-title': str,
        'append-title': yesno,
        'prepend-title': yesno,
        'title-separator': str,
        'default-home': str,
        'default-leaf': str,
        'public': yesno,
    }

def validate_alias_application_form(settings):
    return settings

AliasApplicationFormExtractor.validate = validate_alias_application_form

class AliasApplicationForm(Document):

    extractors = (
            (AliasApplicationFormExtractor, ()),
            )


