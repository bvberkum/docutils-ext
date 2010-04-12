from docutils import Component
from docutils.transforms import universal
from docutils.transforms import frontmatter, references, misc

from dotmpe.du.ext.reader import spec
from dotmpe.du.ext.transform import template, generate, include, specinfo, clean


#MyPHPTemplate = template.TemplateSubstitutions
#MyPHPTemplate.blocks = 
#MyPHPTemplate.format = ""


class Reader(spec.Reader):

    reader_settings_spec = (
            )

    settings_spec = (
            'Example reader for dynamic content (.mpe)',
            None,
            reader_settings_spec +
            specinfo.SpecInfo.settings_spec +
            include.Include.settings_spec +
            template.TemplateSubstitutions.settings_spec +
            generate.PathBreadcrumb.settings_spec +
            generate.Timestamp.settings_spec +
            generate.CCLicenseLink.settings_spec +
            generate.SourceLink.settings_spec +
            clean.StripSubstitutionDefs.settings_spec,
    )
    config_section = 'Template reader'
    config_section_dependencies = ('readers',)

    def get_transforms(self):
        return Component.get_transforms(self) + [
            specinfo.SpecInfo,              # 20
            include.Include,                # 50
            template.TemplateSubstitutions, # 190
#            MyPHPTemplate,
            generate.PathBreadcrumb,        # 200
            generate.Timestamp,             # 200
            generate.SourceLink,            # 200
            generate.CCLicenseLink,         # 200
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
        ]


