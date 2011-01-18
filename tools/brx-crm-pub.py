#!/usr/bin/env python
"""
Publisher for W&S documentation,
based on the Python Docutils publisher.

Use as::

    script-name-{output-format}[.ext]

ie.::

    ws-crm-xhtml
    ws-docs-pdf.py

For arguments see Docutils options in ``--help``.
"""
import os
import sys
try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

import docutils
from docutils import utils, nodes, frontend, io, Component, readers, writers
from docutils.core import Publisher, publish_cmdline
from docutils.readers import doctree
from docutils.readers import standalone
from docutils.transforms import universal, frontmatter, references, misc
from docutils.writers import docutils_xml, pseudoxml

import dotmpe.du.ext # register Du extensions
from dotmpe.du.ext.writer import html, latex2e
from dotmpe.du.ext.transform import generate, include, user, clean,\
    debug # template
from dotmpe.du.ext.extractor import reference



# Brx/WS specific simple extractors
ref_extractor = reference.Extractor            # 900

class Reader(readers.Reader):

    """
    Reader with many transforms in priority range of 20 to 900.
    """

    settings_spec = (
            'Reader with extended set of transforms',
            None,

            standalone.Reader.settings_spec[2] +
            user.UserSettings.settings_spec +
            include.Include.settings_spec +
            #include.RecordDependencies.settings_spec + 
            #template.TemplateSubstitutions.settings_spec +
            generate.PathBreadcrumb.settings_spec +
            generate.Timestamp.settings_spec +
            generate.CCLicenseLink.settings_spec +
            generate.SourceLink.settings_spec +
            clean.StripSubstitutionDefs.settings_spec +
            clean.StripAnonymousTargets.settings_spec +
            debug.Options.settings_spec +
            debug.Settings.settings_spec +
            ref_extractor.settings_spec[2],
    )
    config_section = 'brx-ws extended standalone reader'
    config_section_dependencies = ('readers',)

    def get_transforms(self):
        #return standalone.Reader.get_transforms(self) + [
        return Component.get_transforms(self) + [
            user.UserSettings,              # 20
            include.Include,                # 50
            #include.RecordDependencies,     # 500
            #template.TemplateSubstitutions, # 190
            generate.PathBreadcrumb,        # 200
            generate.Timestamp,             # 200
            generate.SourceLink,            # 200
            generate.CCLicenseLink,         # 200
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
            clean.StripSubstitutionDefs,    # 900
            clean.StripAnonymousTargets,    # 900

            ref_extractor, # 900
        ]



class HtmlWriter(html.Writer):
    def get_transforms(self):
        return html.Writer.get_transforms(self) + [
                ]

class XmlWriter(docutils_xml.Writer):
    def get_transforms(self):
        return docutils_xml.Writer.get_transforms(self) + [
                ]

class LatexWriter(latex2e.Writer):
    def get_transforms(self):
        return latex2e.Writer.get_transforms(self) + [
                ]


## Determine output format from executable filename

output_formats = ('pseudoxml', 'brx_ws_html', 'latex', 'html', 'xml') 
# TODO: support pdf here would be nice

tool = os.path.basename(sys.argv[0])
if '.' in tool:
    tool = tool[:tool.find('.')]
if '-' in tool:
    _names = tool.split('-')
else:
    _names = [tool]

output_format = _names.pop()
if output_format == 'pub':
    output_format = 'pseudoxml'
assert output_format in output_formats, "Cannot handle %s ouput" % output_format

if output_format == 'pseudoxml':
    Writer = pseudoxml.Writer
elif output_format == 'xml':
    Writer = XmlWriter
elif output_format == 'latex':
    Writer = LatexWriter
elif output_format == 'html':
#elif output_format == 'brx_ws_html':
    Writer = HtmlWriter


### 1. Read main document and preprocess to doctree,
###    apply extraction/rewriter transforms.

## Prepare publisher

usage = "%prog [options] [<source> [<destination>]]"
description = ('Reads main document from standalone reStructuredText '
               'from <source> (default is stdin). ')

pub = Publisher(Reader(), None, Writer(), 
    settings=None,
    destination_class=io.NullOutput)

## Get settings for components from command-line

pub.set_components(None, 'rst', None) 
pub.process_command_line(None, None, None, None, {})

## Publish to doctree using reader/parser but without writing

pub.set_writer('null')
null_output = pub.publish(
    None, usage, description, None, None,
    config_section=None, enable_exit_status=1)
document = pub.document

def dump(document):
# these indices are rebuild every time for a document
    from pprint import pformat
    print "Dumping vars for doc ", document['source']
    print 'current_line', pformat(document.current_line)
    #print 'settings', pformat(document.settings)
    print 'reporter', pformat(document.reporter)
    print 'indirect_targets', pformat(document.indirect_targets)
    #print 'substitution_defs', pformat(document.substitution_defs)
    #print 'substitution_names', pformat(document.substitution_names)
    print 'refnames', pformat(document.refnames)
    print 'refids', pformat(document.refids)
    print 'nameids', pformat(document.nameids)
    print 'nametypes', pformat(document.nametypes)
    print 'ids', pformat(document.ids)
    print 'footnote_refs', pformat(document.footnote_refs)
    print 'citation_refs', pformat(document.citation_refs)
    print 'autofootnotes', pformat(document.autofootnotes)
    print 'autofootnote_refs', pformat(document.autofootnote_refs)
    print 'symbol_footnotes', pformat(document.symbol_footnotes)
    print 'symbol_footnote_refs', pformat(document.symbol_footnote_refs)
    print 'footnotes', pformat(document.footnotes)
    print 'citations', pformat(document.citations)
    print 'autofootnote_start', pformat(document.autofootnote_start)
    print 'symbol_footnote_start', pformat(document.symbol_footnote_start)
    print 'id_start', pformat(document.id_start)
    print 'transform_messages', pformat(document.transform_messages)
    print 'transformer', pformat(document.transformer)
    print 'decoration', pformat(document.decoration)
    sys.exit()
#dump(document)

### 2. Render doctree to output format, 
###    apply completion transforms.

pub.source = io.DocTreeInput(document)
pub.destination_class = io.FileOutput
pub.set_destination()

pub.reader = doctree.Reader(parser_name='null')
pub.writer = Writer()

pub.apply_transforms()
output = pub.writer.write(pub.document, pub.destination)
#pub.writer.assemble_parts()


# ----

