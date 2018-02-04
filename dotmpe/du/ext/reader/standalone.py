"""
An Du Reader component with all settings and transforms of the
normal standalone reader, plus new extensions.

Perhaps name this standalone, or find some scheme to dereference links.
"""
from docutils import Component, readers
from docutils.readers import standalone
from docutils.transforms import universal, frontmatter, references, misc
from dotmpe.du.ext.transform import template, generate, include, user, clean,\
    debug, reference, outline


#MyPHPTemplate = template.TemplateSubstitutions
#MyPHPTemplate.blocks =
#MyPHPTemplate.format = ""


class Reader(readers.Reader):

    """
    Reader with many transforms in priority range of 20 to 900.
    """

    supported = ('standalone-mpe', 'mpe')
    """Contexts this reader supports."""

    document = None
    """A single document tree."""

    settings_spec = (
            '.mpe Reader',
            'Standard \'standalone\' reader with extended set of transforms. ',

            standalone.Reader.settings_spec[2] +
            user.UserSettings.settings_spec +
            include.Include.settings_spec +
            #include.RecordDependencies.settings_spec +
            #template.TemplateSubstitutions.settings_spec +
            generate.PathBreadcrumb.settings_spec +
            generate.Timestamp.settings_spec +
            generate.CCLicenseLink.settings_spec +
            generate.SourceLink.settings_spec +
            outline.RecordOutline.settings_spec +
            reference.RecordReferences.settings_spec +
            clean.StripSubstitutionDefs.settings_spec +
            clean.StripAnonymousTargets.settings_spec +
            debug.Options.settings_spec +
            debug.Settings.settings_spec
    )
    config_section = '.mpe extended standalone reader'
    config_section_dependencies = ('readers',)

    def get_transforms(self):
        #return standalone.Reader.get_transforms(self) + [
        return Component.get_transforms(self) + [
            user.UserSettings,              # 20
            include.Include,                # 50
            #include.RecordDependencies,     # 500
            #template.TemplateSubstitutions, # 190
#            MyPHPTemplate,
# TODO: cannot have decorations before DocInfo transform
            generate.PathBreadcrumb,        # 200
            generate.Timestamp,             # 200
            generate.SourceLink,            # 200
            #            generate.CCLicenseLink,         # 200 # FIXME: this interferes with DocInfo
            #tables.TableCaption,            # 210
            #
            references.Substitutions,       # 220
            references.PropagateTargets,    # 260
            frontmatter.DocTitle,           # 320
            frontmatter.SectionSubTitle,    # 340
            frontmatter.DocInfo,            # 340
            references.AnonymousHyperlinks, # 440
            references.IndirectHyperlinks,  # 460
            debug.Settings,                 # 500
            debug.Options,                  # 500
            references.Footnotes,           # 620
            references.ExternalTargets,     # 640
            references.InternalTargets,     # 660
            universal.StripComments,        # 740
            universal.ExposeInternals,      # 840
# Replaced by some generate.* transforms
#            universal.Decorations,         # 820
            misc.Transitions,               # 830
            references.DanglingReferences,  # 850
            outline.RecordOutline,          # 880
            reference.RecordReferences,     # 880
            clean.StripSubstitutionDefs,    # 900
            clean.StripAnonymousTargets,    # 900
        ]


