from __future__ import print_function

from docutils import nodes
import nabu.extract
from nabu.extract import ExtractorStorage

from dotmpe.du import util


class Extractor(nabu.extract.Extractor):

    # XXX: not used by Builder unless staticly hardcoded into its specs.
    settings_spec = (
        'Document Extractor',
        None,
        ((
             'Print source (filename) followed by title. ',
             ['--print-doctitle'], { 'action': 'store_true' }
        ),(
             'Print source (filename, and title if enabled) followed by space-separated source IDs. ',
             ['--print-docid'], { 'action': 'store_true' }
        ),(
             'Print source (filename, and docids if enabled) followed by '
             'comma-separated names. Not applied together with --doc-title. ',
             ['--print-docnames'], { 'action': 'store_true' }
        ),)
    )

    default_priority = 900

    def apply(self, unid=None, storage=None, **kwargs):
        a = (self.document['source'],)
        if self.document.settings.print_docid:
            a += ( " ".join(self.document['ids']), )
        if self.document.settings.print_doctitle:
            a += ( self.document['title'], )
        elif self.document.settings.print_docnames:
            a += ( ", ".join(self.document['names']), )
        print(" ".join(a))

class Storage(ExtractorStorage):
    def __init__(self):
        pass
