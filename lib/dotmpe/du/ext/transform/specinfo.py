"""
It may be helpful to set publisher settings from with a document.

Especially the codec for a file may be scraped from the text before the
publisher has started. 

But only for transforms and the actual writing, settings my be overriden by a
transform. That is what the SpecInfo transform does.

Right now it takes settings from the first or last field-list, but that will
change.
"""
from docutils import transforms, nodes


class SpecInfo(transforms.Transform):

    """
    Override document settings with values from field-list.
    Settings that have been loaded from config or command-line options may be 
    overridden by document author if the ``--spec-names`` option allows it.

    Setting overrides are taken from first and last field-list in the document.

    This should run before another transform if it is to override its settings.
    """

    settings_spec = ((
            'Options explicitly allowed in content to overridde settings.'
#            'Use "*" to override any setting. '
            'IMPORTANT: ``--spec-names`` my be a security risk. '
            'It can also only override settings specific to most transforms '
            'and the writer, as it is to late to influence the reader/parser. ',
            ['--spec-names'], 
            {'default':[], 'action':'append','metavar':'NAME[,NAME]'} 
        #),(
        #    'Discard setting fields from content. '
        #    'This is the default. ',
        #    ['--strip-spec-names'], 
        #    {'dest':'strip_specinfo','action':'store_true',}
        ),(
            'Do not discard setting fields from content. '
            'Default is to strip all named settings. ',
            ['--leave-spec-name'], 
            {'dest':'strip_specinfo', 'default':True, 'action':'store_false',}
        ),(
            'Discard only these fields from content. Multiple values allowed. '
            'Overrides ``--leave-spec-name``. ',
            ['--strip-spec-names'], 
            {'default':[], 'action':'append', 'metavar':'NAME[,NAME]'} 
        ),
    )

    default_priority = 20

    # XXX: there is no proper handling of types here, but one could
    # allow any string value te be set on the settings object

    def apply(self):
        settings = self.document.settings
        if not getattr(settings, 'spec_names'):
            return

        if not hasattr(settings, 'strip_specinfo'):
            settings.strip_specinfo = True

        # parse spec-names option
        spec_names = self._parse_names('spec_names')
        strip_spec_names = self._parse_names('strip_spec_names')

        # get spec-info from first or last field-list
        document = self.document

        field_lists = self.first_and_last_field_list()
        for list in field_lists:
            nodelist = [] 
            for r in self.extract_spec(list):
                if isinstance(r, nodes.field):
                    nodelist.append(r) # keep field
            list[:] = nodelist

    def extract_spec(self, field_list):
        "Extract and strip settings from field_list according to settings. "
        "Return a stripped field_list and a dictionary with settings overrides. "
        settings = self.document.settings

        match_any = '*' in settings.spec_names
        for field in field_list:
            name = field[0][0].astext()
            normedname = nodes.fully_normalize_name(name)
            normedid = normedname.replace('-', '_') # BVB:?

            # TODO: unset uptions are ignored for now
            if not getattr(settings, normedid, ''):
                #assert normedid not in settings.spec_names
                yield field
                continue

            if normedname in settings.strip_spec_names:
                pass#del field_list[i]

            elif settings.strip_specinfo:                
                pass#del field_list[i]

            else:
                yield field
           
            if match_any or normedname in settings.spec_names:
                tp = type(getattr(settings, normedid))
                value = field[1][0][0]
                if tp==int:
                    value = int(value)
                setattr(settings, normedid, value)

    def first_and_last_field_list(self):
        "Returns one or two-part tuple. "
        "FIXME: This is very wastefull, searching the entire doc."
        "Perhaps better require field in decorator or before first paragraph.."
        doc = self.document

        # field_lists may not be in root and frontmatter has not run yet
        field_lists = doc.traverse(nodes.field_list)
        
        if len(field_lists) == 1:
            return (field_lists[0],)

        elif len(field_lists):
            return (field_lists[0], field_lists[-1])

        else:
            return ()
        
    def _parse_names(self, attr): 
        "Read ','-separated values. "
        settings = self.document.settings
        names = [name for name in 
                getattr(settings, attr) if ',' not in name]
        [names.extend(name.split(',')) for name in 
                getattr(settings, attr) if ',' in name]
        setattr(settings, attr, names)



