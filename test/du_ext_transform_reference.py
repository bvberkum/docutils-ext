from __future__ import print_function

import unittest
from StringIO import StringIO

import docutils

import dotmpe.du
from dotmpe.du.ext.transform import reference

from nose_parameterized import parameterized

from du_ext_transform import DotmpeDuExtTransformTest


class DotmpeDuExtTransformReferenceRecordTest(DotmpeDuExtTransformTest):

    @parameterized.expand([
        ( 1, 'var/test-rst.1.document-5.full-rst-demo.rst', (
                'http://www.python.org/',
                'http://www.python.org',
                'http://www.python.org/dev/peps/pep-0287',
                'http://tools.ietf.org/html/rfc2822.html',
                'http://docutils.sourceforge.net/docs/ref/rst/directives.html',
                'mailto:goodger@python.org') ),
        ( 2, 'var/test-rst.5.inline-1.rst', () ),
        ( 3, 'var/test-rst.5.inline-3.rst', () ),
        ( 4, 'var/test-rst.5.inline-4.rst', (
                './ref',
                'http://tools.ietf.org/html/rfc2822.html',
                'http://www.python.org/dev/peps/pep-0287',
                'http://www.python.org',
                'http://www.python.org/',) ),
        ( 5, 'var/test-rst.5.inline-5.rst', (
            '#anonymous-target','#inline-target','#anonymous-inline-target') ),
        ( 6, 'var/test-rst.5.inline-6.rst', ('#test') ),
        ( 7, 'var/test-rst.5.inline-7.rst', (
            'trgt1', '#test') ),
        ( 8, 'var/test-rst.24.references.rst', (
            './ref','http://www.python.org/',) ),
        # XXX: maybe just include set of all rSt test-files, or at least those
        # valid ones and test on those..
    ])
    def test_1(self, tstnr, doc_file, expected):
        f = StringIO()

        doctree = self._publish_file(doc_file, reader_name='mpe',
                # FIXME: mix/match spec somehow
            #settings_spec = reference.RecordReferences,
            #(
            #    'test', None, reference.RecordReferences.settings_spec
            #),
            settings_overrides = {
                'rfc_references': True,
                'rfc_base_url': 'http://tools.ietf.org/html/',
                'record_references': True,
                'record_outgoing_refs': ['reference'],
                'records': f
            })
        self.assert_(doctree.settings.record_references)
        self.assert_(doctree.settings.record_outgoing_refs)

        xform = reference.RecordReferences(doctree)
        xform.apply()
        results = xform.finish()
        for j, rs in enumerate(results):
            self.assert_(rs in expected, "%i. %i. %s" % ( tstnr, j, rs) )


if __name__ == '__main__':
    unittest.main()
