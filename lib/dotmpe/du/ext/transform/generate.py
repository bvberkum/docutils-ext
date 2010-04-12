""":created: 2010-04-11
:author: B. van Berkum

Transforms generate and insert content at publication time.

The breadcrumb is a navigational aid output somewhere usually before the
content.
"""
import os
from docutils import nodes
from docutils.transforms import Transform
from docutils.transforms.references import Substitutions
from dotmpe.du.ext.transform import include


"This should run before references.Substitutions (220). "
"200 places them after template.TemplateSubstitutions "
"and before the earliest transform (misc.ClassAttribute at 210). "

class PathBreadcrumb(include.Include):

    "Insert a substitution definition into the document tree, "
    "and a substitution reference if needed. "

    default_priority = 200

    settings_spec = (
            (
                'Add the breadcrumb to the document. '
                'If the substitution reference is not present, append to header.',
                ['--breadcrumb'], 
                {'action':'store_true', 'default': False}
            ),(
                'Never include the breadcrumb. '
                'Strip substitution reference if found.',
                ['--no-breadcrumb'], 
                {'dest':'breadcrumb','action':'store_false'}
            ),(
                'Generate breadcrumb from path (default: document source path)', 
                ['--breadcrumb-path'], 
                {'metavar': 'PATH'}
            ),(
                'Insert breadcrumb substitution reference if it is not there at ' 
                'given location (default: %default). ', 
                ['--breadcrumb-location'], 
                {'default':'header', 'metavar':'DECORATOR_OR_XPATH'}
            ),(
                'Rename the substitution reference to use for the breadcrumb. '
                '(default: %default) '
                'This may can cause --breadcrumb-location to be ignored if the '
                'document already has the substitution reference. ', 
                ['--breadcrumb-substitution-reference'], 
                {'default':'breadcrumb', 'metavar':'REFNAME'}
            ))

    def apply(self):
        if not self.document.settings.breadcrumb:
            return

        subrefname = nodes.fully_normalize_name(
            self.document.settings.breadcrumb_substitution_reference)
        subrefid = nodes.make_id(subrefname)

        subreflist = self.document.traverse(nodes.substitution_reference)
        
        if subrefname not in subreflist:
            subloc = self.find_breadcrumb_location()

            # append sub. reference at location
            subrefnode = nodes.substitution_reference(None, subrefname)
            subrefnode['refname'] = subrefname
            subloc.append(subrefnode)
            self.document.note_substitution_ref(subrefnode, subrefname)

        breadcrumb = self.generate_breadcrumb()
        # append sub. definition to document
        subdefnode = nodes.substitution_definition()
        subdefnode.append(breadcrumb)
        subdefnode['names'].append(subrefname)
        self.document.append(subdefnode)
        self.document.note_substitution_def(subdefnode, subrefname) 

    def find_breadcrumb_location(self):
        subloc = self.document.settings.breadcrumb_location
        decoration = self.document.get_decoration()
        if hasattr(decoration, 'get_'+subloc):
            loc = getattr(decoration, 'get_'+subloc)()
        else:
            loc = self.find_location(subloc)
        return loc

    def generate_breadcrumb(self):
        "Generate ordered and linked 'breadcrumb' path list. "

        #sep = self.document.settings.breadcrumb_path_separator
        sep = '/'
        path = getattr(self.document.settings, 'breadcrumb_path')
        if not path:
            path = self.document['source']

        breadcrumb = nodes.enumerated_list()

        dir, name = os.path.split(path)
        dirs = dir.split(sep) or []
       
        _p = []
        while dirs:
            dn = dirs.pop(0)
            _p.append(dn)
            ref = nodes.reference('', nodes.Text("%s%s" % (dn, sep)), 
                refuri=sep.join(_p)+sep)
            p = nodes.paragraph('', '', ref)
            item = nodes.list_item()
            item.append(p)
            breadcrumb.append(item)
        p = nodes.paragraph('', '', nodes.Text(name))
        item = nodes.list_item()
        item.append(p)
        breadcrumb.append(item)

        return breadcrumb

# TODO:

class Generated(include.Include):

    """
    Alternative decorator to handle the following front-end options:

    --date, -d              Include the date at the end of the document (UTC).
    --time, -t              Include the time & date (UTC).
    --no-datestamp          Do not include a datestamp of any kind.
    """

    "universal.Decorations usually generates some footer data faily late in the "
    "publishing and depending on settings. "

    settings_spec = (
            )

    default_priority = 200
    "Run much earlier than the original header/footer generator at 820. "
    "This overrides substitutions so run before 220. "


class SourceLink(include.Include):
    
    settings_spec = (
            )

    default_priority = 200
    "Run much earlier than the original header/footer generator at 820. "
    "This overrides substitutions so run before 220. "

