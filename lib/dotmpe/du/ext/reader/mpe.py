from docutils import Component
from docutils.transforms import universal
from docutils.transforms import frontmatter, references, misc

from dotmpe.du.ext.reader import spec
from dotmpe.du.ext.transform import template, generate, include


#MyPHPTemplate = template.TemplateSubstitutions
#MyPHPTemplate.blocks = 
#MyPHPTemplate.format = ""

reader_settings_spec = (
        )

class Reader(spec.Reader):

    settings_spec = (
            'Example reader for dynamic content',
            None,
            reader_settings_spec +
            include.Include.settings_spec +
            template.TemplateSubstitutions.settings_spec +
            generate.PathBreadcrumb.settings_spec +
            generate.Generated.settings_spec +
            generate.SourceLink.settings_spec,
    )
    config_section = 'Template reader'
    config_section_dependencies = ('readers',)

    def get_transforms(self):
        return Component.get_transforms(self) + [
            include.Include,                
            universal.ExposeInternals,
# Generated footer is replaced by some generate.* transforms
#            universal.Decorations,
# Not supported:
#            universal.StripComments
            template.TemplateSubstitutions,
            generate.PathBreadcrumb,
            generate.Generated,
            generate.SourceLink,
#            MyPHPTemplate,
            references.Substitutions,
            references.PropagateTargets,
            frontmatter.DocTitle,
            frontmatter.SectionSubTitle,
            frontmatter.DocInfo,
            references.AnonymousHyperlinks,
            references.IndirectHyperlinks,
            references.Footnotes,
            references.ExternalTargets,
            references.InternalTargets,
            references.DanglingReferences,
            misc.Transitions,
            ]


