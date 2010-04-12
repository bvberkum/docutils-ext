from dotmpe.du.ext.transform import include


class TemplateSubstitutions(include.Include):

    "Insert raw nodes into the tree. "

    settings_spec = (
        ('Load substitution definitions from CSV file. ', 
            ['--template-definitions'], {'default':'var/template'}),
        ('Substitute only named fields. Multiple allowed. ', 
            ['--template-fields'], {'metavar':'FIELD', 'action':'append'}),
        ('Output format for template var. ', 
            ['--template-language'], {'choices':['php']}),
    )

    default_priority = 190

    def apply(self):
        pass
        


