""":created: 2010-04-11
:author: B. van Berkum

These transforms generate and insert content at publication time.

The breadcrumb is a navigational aid output somewhere usually before the
content.
"""
import os, urlparse
from docutils import nodes
from docutils.transforms import Transform
from docutils.transforms.references import Substitutions
from dotmpe.du.ext.transform import include


# This should run before references.Substitutions (220). "
# 200 places them after template.TemplateSubstitutions "
# and before the earliest transform (misc.ClassAttribute at 210). "

class PathBreadcrumb(include.Include):

    "Insert a substitution definition into the document tree, "
    "and a substitution reference if needed. "

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
                'Generate breadcrumb from path (default: document source path). ',
#                'NOTE: if it is not absolute, a "/" is prefixed to it.', 
                ['--breadcrumb-path'], 
                {'metavar': '<PATH>'}
            ),(
                'Insert breadcrumb substitution reference if it is not there, at ' 
                'given location (default: %default). ', 
                ['--breadcrumb-location'], 
                {'default':'header', 'metavar':'<DECORATOR_OR_XPATH>'}
            ),(
                'Rename the substitution reference to use for the breadcrumb. '
                '(default: %default) '
                'This may can cause --breadcrumb-location to be ignored if the '
                'document already has the substitution reference. ', 
                ['--breadcrumb-substitution-reference'], 
                {'default':'breadcrumb', 'metavar':'<REFNAME>'}
            ))

    default_priority = 200

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
        return self.find_location(subloc)

    def generate_breadcrumb(self):
        "Generate ordered and linked 'breadcrumb' path list. "

        #sep = self.document.settings.breadcrumb_path_separator
        sep = '/'
        path = getattr(self.document.settings, 'breadcrumb_path')
        if not path:
            path = self.document['source']

        breadcrumb = nodes.enumerated_list(classes=['breadcrumb'])

        # TODO: much more customization, what about domain, etc?
        s,h,path,para,q,f = urlparse.urlparse(path)
        dirs = path.split(sep) or []
       
        _p = []
        while dirs:
            dn = dirs.pop(0)
            _p.append(dn)
            if dirs:
                href = sep.join(_p) or sep
                # XXX: fix the path to be absolute
                if not href.startswith(sep):
                    href = sep+href
                dn += sep
                ref = nodes.reference('', nodes.Text(dn), refuri=href)
            else:
                ref = nodes.Text(dn)
            p = nodes.paragraph('', '', ref)
            item = nodes.list_item()
            item.append(p)
            breadcrumb.append(item)

        return breadcrumb


def validate_cc_license(setting, value, option_parser, 
        config_parser=None, config_section=None):
    l = CCLicenseLink.licenses
    for v in value.split('-'):
        if v not in l:
            option_parser.error("Illegal license %s in %s" % (v, value))
        else:
            l = l[v]
    return value            

class CCLicenseLink(include.Include):

    licenses = {
        'pd': (),
        'by': {
            'sa': (),
            'nd': (),
            'nc': {
                'nd': (),
                'sa': ()
            }
        }
    }

    settings_spec = ((
           'Embed Creative Commons License link. ',
           ['--cc'],
           {'action':'store_true', 'dest':'cc_embed'}
       ),(
           'Explicitly disallow Creative Commons License link. ',
           ['--no-cc'],
           {'action':'store_false', 'dest':'cc_embed'}
       ),(
           'Link format for Creative Commons License. ',
           ['--cc-link'],
           {'default': 'http://creativecommons.org/licenses/%s/3.0', 
            'metavar':'<URL>'}
       ),(
           'Creative Commons License. Licenses may be combined, separate by "-". '
           '(default: %default). ',
           ['--cc-license'],
           {'default': 'pd', 'choices':['pd','sa','nc','nd','by'], 
               'validator': validate_cc_license, 'metavar': '<LICENSE>' }
       ),(
           'Insert cc-license substitution reference if it is not there at ' 
           'given location (default: %default). ', 
           ['--cc-license-location'], 
           {'default':'footer', 'metavar':'<DECORATOR_OR_XPATH>'}
       ),(
           'Rename the substitution reference to use for the cc-license. '
           '(default: %default) '
           'This may can cause --cc-license-location to be ignored if the '
           'document already has the substitution reference. ', 
           ['--cc-license-substitution-reference'], 
           {'default':'cc-license', 'metavar':'<REFNAME>'}
       ))

    default_priority = 200

    def apply(self):
        settings = self.document.settings
        if not settings.cc_embed:
            return

        subrefname = nodes.fully_normalize_name(
                settings.cc_license_substitution_reference)
        subrefid = nodes.make_id(subrefname)
        subrefpath = nodes.fully_normalize_name(
                settings.cc_license_location)

        subreflist = self.document.traverse(nodes.substitution_reference)
        if subrefname not in subreflist:
            subrefloc = self.find_location(subrefpath)

            # append sub. ref. at location
            subrefnode = nodes.substitution_reference(None, None,
                    refname=subrefname)
            subrefloc.append(subrefnode)
            self.document.note_substitution_ref(subrefnode, subrefname)

        license = self.generate_cc_license()
        # append sub. def. to document
        subdefnode = nodes.substitution_definition(names=subrefname)
        subdefnode.append(license)
        self.document.append(subdefnode)
        self.document.note_substitution_def(subdefnode, subrefname)

    def generate_cc_license(self):
        license = self.document.settings.cc_license.replace(' ', '-')
        descr = license.replace('-', ' ')#.title()
        href = self.document.settings.cc_link % license

        return nodes.paragraph('', '', nodes.reference('', descr, refuri=href))


# TODO:

class Timestamp(include.Include):

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

    def apply(self):
        settings = self.document.settings
        #print 'timestamp', settings.datestamp

    def generate_timestamp(self):
        pass


class SourceLink(include.Include):
    
    settings_spec = (
            )

    default_priority = 200

    def apply(self): pass

