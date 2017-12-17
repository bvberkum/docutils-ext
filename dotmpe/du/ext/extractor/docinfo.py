from __future__ import print_function
import sys, time, datetime, calendar

from docutils import nodes
import nabu.extract
from nabu.extract import ExtractorStorage

from dotmpe.du import util


def parse_datetime(value, formats=util.datetime_formats):
    for fmt in formats:
        e = None
        try:
            return datetime.datetime.strptime( value, fmt )
        except ValueError as e:
            continue
        raise e

def find_docinfo_datetime(document, field):
    """
    Retrieve datetime from docinfo field in document.
    """
    for e in document.children:
        if isinstance( e, nodes.docinfo, ):
            for c in e.children:
                if field in c.children[0].astext().lower():
                    return parse_datetime(c.children[1].astext())

class Extractor(nabu.extract.Extractor):

    """
    """

    # XXX: not used by Builder unless staticly hardcoded into its specs.
    settings_spec = (
        'Document Extractor',
        None,
        ((
             'Print source (filename) followed by title. Prints "(untitled)" if '
             'no document title is available.',
             ['--print-doctitle'], { 'action': 'store_true' }
        ),(
             'Print source (filename, and title if enabled) followed by '
             'space-separated source IDs, or "none" if no Id was generated. ',
             ['--print-docid'], { 'action': 'store_true' }
        ),(
             'Print source (filename, and docids if enabled) followed by '
             'comma-separated names. Not applied together with --doc-title. ',
             ['--print-docnames'], { 'action': 'store_true' }
        ),(
             'Print created datetime (from docinfo) after source (filename)',
             ['--print-created'], { 'action': 'store_true' }
        ),(
             'Print updated datetime (from docinfo) after source (filename)',
             ['--print-updated'], { 'action': 'store_true' }
        ),(
             '',
             ['--no-db'], { 'action': 'store_true' }
        ),)
    )

    default_priority = 900

    def apply(self, unid=None, storage=None, **kwargs):
        a = (self.document['source'],)
        if self.document.settings.print_docid:
            ids = self.document['ids']
            if ids: a += ( ",".join(ids), )
            else: a += ( "(none)", )
        if self.document.settings.print_created:
            created = find_docinfo_datetime(self.document, 'created')
            if created: a += ( created.strftime(util.ISO_8601_DATETIME), )
            else: a += ( "(none)", )
        if self.document.settings.print_updated:
            updated = find_docinfo_datetime(self.document, 'updated')
            if updated: a += ( updated.strftime(util.ISO_8601_DATETIME), )
            else: a += ( "(none)", )

        if self.document.settings.print_doctitle:
            if 'title' in self.document: a += ( self.document['title'], )
            else: a += ( "(untitled)", )
        elif self.document.settings.print_docnames:
            a += ( ",".join(self.document['names']), )

        print(u" ".join(a))


class Storage(ExtractorStorage):
    def __init__(self):
        pass
