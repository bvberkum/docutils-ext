"""
:Created: 2018-01-28

Record references.

Usage::

    $ python tools/rst2pprint \
            --record-references=/tmp/ref.list \
            --record-reference-format=todo.txt \
            document.rst /dev/null

"""
from docutils import transforms, nodes
from dotmpe.du import mpe_du_util as util



class RecordReferences(transforms.Transform):

    settings_spec = (
        (
            'Record references to file',
            ['--record-references'],
            {'default':None, 'metavar':'FILE' }
        ), (
            'Append recorded references to file iso. truncating existing file',
            ['--append-reference-records'],
            {'default':False, 'action':'store_true' }
        ), (
            'Format for references file: url, text or todo.txt. ',
            ['--record-reference-format'],
            {'default': 'url', 'metavar':'NAME' }
        ), (
            # TODO: include inline types at ref targets?
            'Reference types to include. ',
            ['--record-reference-types'],
            {'default':['reference'], 'action':'append', 'metavar':'NAME[,NAME]',
                'validator': util.validate_cs_list }
            #reference'',
            #citation_reference,
            #footnote_reference,
            #substitution_reference,
            #title_reference
        ),
    )

    default_priority = 880

    def apply(self):
        settings = self.document.settings
        if not getattr(settings, 'record_references', None):
            return

        self.format = settings.record_reference_format
        self.types = settings.record_reference_types

        ref_tags = [ getattr(nodes, t) for t in self.types ]

        mode = settings.append_reference_records and 'a+' or 'w+'
        self.f = open(settings.record_references, mode)
        for ref_type in ref_tags:
            for ref in self.document.traverse(ref_type):
                self._record_reference(ref_type, ref)

    def _record_reference(self, ref_type, ref):

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
