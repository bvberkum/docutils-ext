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

        subdefs = doc.traverse(nodes.substitution_definition)
        for e in subdefs:
            e.parent.remove(e)


class StripAnonymousTargets(transforms.Transform):

    """
    Strip anonymous target (definitions) from the doc-tree.
    """

    settings_spec = ((
            'Strip anonymous targets. ',
            ['--strip-anonymous-targets'], 
            {'default':False, 'action':'store_true'} 
        ),
        )

    default_priority = 900

    def apply(self):
        doc = self.document

        if not getattr(doc.settings, 'strip_anonymous_targets', ''):
            return

        trgts = doc.traverse(nodes.target)
        for t in trgts:
            if t['anonymous']:
                t.parent.remove(t)

