from docutils import transforms, nodes


class StripSubstitutionDefs(transforms.Transform):

    """
    Strip substitutions definitions from the doc-tree.
    """

    settings_spec = ((
            'Strip substitution definitions. ',
            ['--strip-substitution-definitions'], 
            {'default':False, 'action':'store_true'} 
        ),
        )

    default_priority = 900

    def apply(self):
        doc = self.document

        if not getattr(doc.settings, 'strip_substitution_definitions', ''):
            return

        for i in range(0, len(doc)):
            e = doc[i]
            if isinstance(e, nodes.substitution_definition):
                del doc[i]

