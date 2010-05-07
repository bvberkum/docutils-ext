import itertools
from dotmpe.du import util
from dotmpe.du.ext.transform import include


class TemplateSubstitutions(include.Include):

    "Insert raw nodes into the tree. "

    settings_spec = (
        ('Load substitution definitions from CSV file. ', 
            ['--template-definitions'], 
            {'default':'var/template','metavar':'FILE','dest':'template_file'}),

        ('Add a single substitution definition. ', 
            ['--template-definition'], 
            {'action':'append','default':[],'metavar':'REF[,TYPE,TRIML,TRIMR],DATA'}),

        ('Substitute only named fields. Multiple allowed. '
         'Defaults to all fields defined by --template-definition(s).', 
            ['--template-fields'], {'metavar':'FIELD',
                'action':'append','default':[], 'validator':util.cs_list}),

        # ('Output format for template var. ', 
        #    ['--template-language'], {'choices':['php']}),
    )

    default_priority = 190

    def apply(self):
        settings = self.document.settings

        fieldnames = [name for name in 
                settings.template_fields if ',' not in name]
        [fieldnames.extend(name.split(',')) for name in 
                settings.template_fields if ',' in name]

        pairs = [td.split(',') for td in settings.template_definition]

        if settings.template_file:
            pass # pairs += 

        


