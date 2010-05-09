"""
Builders for Blue Lines.
"""
import logging
import docutils
from docutils import readers, writers, Component
from docutils.transforms import universal, references
from dotmpe.du import builder, util, form
from dotmpe.du.ext.reader import mpe
from dotmpe.du.ext.writer import xhtmlform
from dotmpe.du.ext.transform import generate, form1
from dotmpe.du.ext.extractor import form2


logger = logging.getLogger(__name__)

class Document(builder.Builder):

    settings_overrides = {
        # overridden by bluelines.server:
        #'template': os.path.join(conf.ROOT, 'du-template.txt'),

        # Doctree inclusions
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

    extractors = [
        #(reference.Extractor, reference.ReferenceStorage()),
        #(extractors.Contact
        #(extractor.docinfo, extractor.docinfo)
    ]

    settings_spec = (
            'Blue Lines Document settings. ',
            None, ()
            )

    class Reader(mpe.Reader):
        supported = ('bluelines',)
        def get_transforms(self):
            return mpe.Reader.get_transforms(self)


def builder_module_name(node):
    logger.info('TODO: %s', node)
    return node.astext()

def alias_user_reference(node):
    logger.info('TODO: %s', node)
    return node.astext()


class FormPage(Document):

    extractors = [
        (form2.FormExtractor, form2.FormStorage),
    ]

    settings_spec = (
        'Blue Lines Form settings.  ',
        None, 
        form.FormProcessor.settings_spec + 
        form2.FormExtractor.settings_spec
            )

    class Reader(readers.Reader):
        settings_spec = (
            'Blue Lines form-page reader. ',
            None,
            form.FormProcessor.settings_spec + 
            form1.DuForm.settings_spec 
                )
        config_section = 'Blue Lines reader'
        config_section_dependencies = ('readers',)

        def get_transforms(self):
            return Component.get_transforms(self) + [ 
                generate.Timestamp,         # 200
                form1.DuForm ,              # 500
                    ]

    class Writer(xhtmlform.Writer):
        pass


class AliasFormPage(FormPage):

    """
    After the initial read/parse this should deliver a doctree with all fields
    converted and validated into a Values instance.

    The document may be written to XHTML, while the extracted 
    """

    settings_spec = FormPage.settings_spec

    settings_overrides = {
        'form_fields': {
            'owner': (alias_user_reference,),
            'build': (builder_module_name,),
            'default-title': (util.du_str,),
            'append-title': (util.yesno,),
            'prepend-title': (util.yesno,),
            'title-separator': (util.du_str,),
            'default-home': (util.du_str,),
            'default-leaf': (util.du_str,),
            'public': (util.yesno,),
        },
        #'form_store': form2.FormStorage,
    }


class UserFormPage(FormPage):

    settings_spec = FormPage.settings_spec

    settings_overrides = { }


if __name__ == '__main__':
    if sys.argv[1:]:
        source_id = sys.argv[1]
    else:
        source_id = os.path.join(example_dir, 'form.rst')
    source = open(source_id).read()

    builder = AliasFormPage()
    builder.initialize()
    document = builder.builder(source, source_id)

    builder.prepare()
    builder.process(document, source_id)

