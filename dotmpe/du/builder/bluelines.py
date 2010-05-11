"""
Builders for Blue Lines.
"""
import logging
import docutils
from docutils import readers, writers, Component, nodes
from docutils.transforms import universal, references, frontmatter, misc
from dotmpe.du import builder, util, form
from dotmpe.du.ext.reader import mpe
from dotmpe.du.ext.writer import xhtmlform
from dotmpe.du.ext.transform import generate, form1, clean
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


# custom convertors
def builder_module_name(node):
    logger.info('TODO: %s', node)
    return node.astext()

def alias_user_reference(node):
    "Return user email. "
    assert isinstance(node, nodes.paragraph)
    assert isinstance(node[0], nodes.reference)
    return node[0]['refuri']

def alias_reference(node):
    "Return alias handle. "
    pass
    return node.astext()


class FormPage(Document):

    extractors = [
        (form2.FormExtractor, form2.FormStorage),
    ]

    settings_spec = (
        'Blue Lines Form settings.  ',
        None, 
        form.FormProcessor.settings_spec
            )

    class Reader(readers.Reader):
        settings_spec = (
            'Blue Lines form-page reader. ',
            None,
                (),
            )
        config_section = 'Blue Lines reader'
        config_section_dependencies = ('readers',)

        def get_transforms(self):
            return readers.Reader.get_transforms(self) + [ 
                generate.Timestamp,         # 200
                form1.DuForm ,              # 500

                references.Substitutions,       # 220
                references.PropagateTargets,    # 260
                frontmatter.DocTitle,           # 320
                frontmatter.SectionSubTitle,    # 340
                frontmatter.DocInfo,            # 340
                references.AnonymousHyperlinks, # 440
                references.IndirectHyperlinks,  # 460
                references.Footnotes,           # 620
                references.ExternalTargets,     # 640
                references.InternalTargets,     # 660
                universal.StripComments,        # 740
                universal.ExposeInternals,      # 840
    # Replaced by some generate.* transforms
    #            universal.Decorations,         # 820
                misc.Transitions,               # 830
                references.DanglingReferences,  # 850
                clean.StripSubstitutionDefs,    # 900
                clean.StripAnonymousTargets,    # 900
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
        'form_fields_spec': [
            ('handle', alias_reference,),
            ('owner', alias_user_reference,),
            ('build', builder_module_name, { 'required': False }),
            ('default-title', 'str', { 'required': False }),
            ('append-title', 'yesno', { 'required': False }),
            ('prepend-title', 'yesno', { 'required': False }),
            ('title-separator', 'str', { 'required': False }),
            ('default-home', 'str', { 'required': False }),
            ('default-leaf', 'str', { 'required': False }),
            ('public', 'yesno',),
        ],
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

