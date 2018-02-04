"""
:Created: 2018-01-28

Simple reference 'extractor' without use of additional extractor API, only
extending Transform and using line-based plain-text formats for recording.

TODO: see dotmpe.du.ext.extractor.reference to supplement API?

Transforms:
    RecordReferences
        Record references to file, looks at all references for URI's and outputs.


Usage with .mpe Reader::

    $ python tools/rst2pprint \
            --record-references=/tmp/ref.list \
            --record-reference-format=todo.txt \
            document.rst /dev/null

"""
from __future__ import print_function

from docutils import transforms, nodes
from dotmpe.du import mpe_du_util as util



class RecordReferences(transforms.Transform):

    """
    Write references from document to file.

    This attempts to resolve all references or 'HTML links' for the document.
    The URLs are written to the file argument, optionally with the local span of
    text or other fields according to output format.

    References come in two basic types:

    - Incoming links or reference targets
    - Outgoing links or (plain) references

    Which document elements correspond to what type and how it is represented
    may vary and so can be configured.

    For now only outgoing plain references are written in one of three simple
    plain text formats.

    An open file can be provided to apply, to let the recorder run in customized
    subclasses, or other than docutils.Reader instance parts.
    E.g. HtdocsExtractor.

    Outgoing
    --------
    For outgoing links, the obvious candidate is one specific
    ``docutils.node.Referential`` type and then only those that have a
    ``refuri`` to outside the homedoc.

    TODO: Additionally, first cites and titles, and then perhaps other roles
    or any random block with a simple text span becomes a candidates to create
    outgoing links.

    Incoming
    --------
    TODO: Many doc-parts can be targetted.
    """

    relative_path_settings = ()
    settings_spec = (
        (
            'Record references to file',
            ['--record-references'],
            {'default':None, 'metavar':'FILE' }
        ), (
            'Record outgoing references (default: %s). Disable by clearing. ',
            ['--record-outging-refs'],
            {'default':['reference'], 'action':'append', 'metavar':'NAME[,NAME]',
                'validator': util.validate_cs_list }
        ), (
            'Record (incoming) reference targets (default: %s). Disable by clearing. ',
            ['--record-incoming-refs'],
            {'default':[], 'action':'append', 'metavar':'NAME[,NAME]',
                'validator': util.validate_cs_list }
        ), (
            'Append recorded references to file iso. truncating existing file',
            ['--append-reference-records'],
            {'default':False, 'action':'store_true' }
        ), (
            'Format for references file: url, text or todo.txt. ',
            ['--record-reference-format'],
            {'default': 'url', 'metavar':'NAME' }
        ), (
            'Dont record references, even if file was given. ',
            ['--no-references-record'], { 'dest': 'record_references', 'action': 'store_false' }
        ),
    )

    default_priority = 880

    def apply(self, f=None):
        g = self.document.settings
        if not getattr(g, 'record_references', None):
            return

        if getattr(g, 'records', None):
            f = g.records

        if f:
            self.f = g.records
        else:
            mode = g.append_reference_records and 'a+' or 'w+'
            self.f = open(g.record_references, mode)

        if getattr(g, 'record_outgoing_refs', None):

            self.format = g.record_reference_format
            self.types = g.record_outgoing_refs

            ref_tags = [ getattr(nodes, t) for t in self.types ]

            for ref_type in ref_tags:
                for ref in self.document.traverse(ref_type):
                    self._record_reference(ref_type, ref)

        if getattr(g, 'record_incoming_refs', None):
            pass # TODO: record-incoming-refs

    def finish(self):
        self.f.seek(0)
        results = [ l.strip() for l in self.f.readlines() ]
        return results

    def _record_reference(self, ref_type, ref):

        if not 'refuri' in ref:
            # TODO: warn no refuri
            return

        if self.format == 'url':
            line = ref['refuri']

        elif self.format == 'text':
            if 'anonymous' in ref: line = ref['refuri']
            elif 'name' not in ref: line = ref['refuri']
            else: line = ref['refuri'] +'  '+ ref['name']

        elif self.format == 'todo.txt':
            line = "<%s>" % ref['refuri']
            at = dict(ref.attlist())
            del at['refuri']
            if 'name' in at:
                line = at['name']+' '+line
                del at['name']
            for k, v in at.items():
                line += ' %s:%s' % ( k, v )

        self.f.write(line+'\n')
