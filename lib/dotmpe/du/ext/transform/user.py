"""
It may be helpful to set publisher settings from within a document.

Especially the codec for a file may be scraped from the text before the
publisher has started. Nabu does this for the document's ID. I myself use some
fields the establish what reader to use.

But settings my be overriden by a transform only for later and the actual writing.
That is what the SpecInfo transform does.

Right now it takes settings from the first or last field-list, but that will
change.
"""
from docutils import transforms, nodes
from dotmpe.du import util


class UserSettings(transforms.Transform):

    """
    Override document settings with values from a field-list. However, the field 
    list(s) must be in a decorator (header, footer, margin) or in the first list
    of the document (the latter also used in the docinfo transforms).

    Settings that have been loaded from config or command-line options may be 
    overridden by the document author if the ``--user-settings`` option lists
    it. Ofcourse, the normal Du frontend may be used to inspect the options of a
    particular publisher configuration.

    This should run before another transform if it is to override its settings.
    Meaning it will never override options used while either parsing or reading.

    The default priority of this transform should put it before any other
    standard Du transform.
    """

    settings_spec = (
        (
            'Allow settings overrides by document author, extract fields for '
            'the given names. '
            'Important! ``--user-settings`` poses a security risk. '
            'Also, it can *only* override settings specific to most transforms '
            'and the writer, as it runs too late to influence the reader/parser. ',
            ['--user-settings'], 
            {'default':[], 'action':'append','metavar':'NAME[,NAME]',
                'validator': util.validate_cs_list } 
        ),(
            'Discard settings overrides fields from content. '
            'This is the default. ',
            ['--strip-user-settings', '--strip-settings'], 
            {'dest':'strip_user_settings', 'default':True, 'action':'store_true',}
        ),(
            'Do not discard setting fields from content. '
            'Default is to strip all named settings. ',
            ['--leave-user-settings', '--leave-settings'], 
            {'dest':'strip_user_settings', 'action':'store_false',}
        ),(
            'Always these fields from content. Multiple values allowed. ',
            ['--strip-settings-names'], 
            {'default':[], 'action':'append', 'metavar':'NAME[,NAME]',
                'validator': util.validate_cs_list } 
        ),
    )

    default_priority = 20

    def apply(self):
        settings = self.document.settings
        if not getattr(settings, 'user_settings'):
            return

        if not hasattr(settings, 'strip_user_settings'):
            settings.strip_user_settings = True

        # Parse name lists and update document.settings
        self._parse_names('user_settings')
        self._parse_names('strip_settings_names')

        # get our canditate fields from document
        document = self.document
        field_lists = self.candidate_field_lists()
        if not field_lists:
            print 'info: settings but no field-lists'
            return
        for list in field_lists:
            nodelist = [] 

            # scan the list, process recognized settings 
            # and filter stripped fields, rewrite tree
            for r in self.extract_spec(list):
                if isinstance(r, nodes.field):
                    nodelist.append(r) # keep field
            if not nodelist:
                list.parent.remove(list)
            else:    
                list[:] = nodelist

    def find_setting(self, name):
        pass # TODO: need access to option_parser here.

    def extract_spec(self, field_list):
        "Extract and strip settings from field_list according to settings. "
        "Return a stripped field_list and a dictionary with settings overrides. "
        settings = self.document.settings

        match_any = False#'*' in settings.spec_names
        for field in field_list:
            name = field[0][0].astext()
            normedname = nodes.fully_normalize_name(name)
            normedid = normedname.replace('-', '_') # BVB:?

            print name, normedname, normedid
            self.find_setting(normedid)

            if normedname in settings.strip_settings_names:
                pass#del field_list[i]

            elif settings.strip_settings_names:                
                pass#del field_list[i]

            else:
                #assert normedid not in settings.spec_names
                yield field

            if not getattr(settings, normedid, ''):
            # TODO: unset uptions are ignored for now
                continue
          
            print normedname, normedname in settings.spec_names
            print normedid, normedid in settings.spec_names

            if match_any or normedname in settings.spec_names:
                self.find_setting(normedname)
                tp = type(getattr(settings, normedid))
                value = field[1][0][0]
                if tp==int:
                    value = int(value)
                setattr(settings, normedid, value)

    def candidate_field_lists(self):
        return self.document.traverse(nodes.field_list)
    #
        "Returns at most five lists, from header, margin left/right, footer "
        "and/or the first from the document body."
        deco = self.document.get_decorator()
        for node in (deco.get_header(), deco.get_footer()):
            if isinstance(node, nodes.field_list):
                pass#yield node
        
    def _parse_names(self, attr): 
        "Read ','-separated values. "
        settings = self.document.settings
        names = [name for name in 
                getattr(settings, attr) if ',' not in name]
        print '_parse_names', names

        [names.extend(name.split(',')) for name in 
                getattr(settings, attr) if ',' in name]
        setattr(settings, attr, names)



