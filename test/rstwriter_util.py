import unittest

from dotmpe.du.ext.writer import rst


class RstTranslatorUnitTest(unittest.TestCase):

    def test_current_whitespace(self):
        class Doc(object):
            settings = None
        w = rst.RstTranslator(Doc())

        bodies = [
            ([' '], ' '),
            (['test test test '], ' '),
            (['test\t',' ','test '], ' '),
            ([' ','\ttest', '\n', ' ', '\t\n'], '\n \t\n'),
            ([' ','\ttest', ' \r\n', '', '\t   ','\t\n'], ' \r\n\t   \t\n'),
            (['  test  '], '  '),
        ]
        for i, o in bodies:
            w.body = i
            r = w.current_whitespace # instance property under test
            self.assertEqual(r, o, "Mismatch for input %r, expected %r but got %r" % (i, o, r))

    def test_assure_newline(self):
        class Doc(object):
            settings = None
        w = rst.RstTranslator(Doc())

        # XXX: not stripping trailing ws, read source
        bodies = [
            ([' '], ' \n'),
            (['test test test '], ' \n'),
            (['test\t',' ','test '], ' \n'),
            ([' ','\ttest', '\n', ' ', '\t\n'], '\n \t\n'),
            ([' ','\ttest', ' \r\n', '', '\t   ','\t\n'], ' \r\n\t   \t\n'),
            (['  test  '], '  \n'),
        ]
        for i, o in bodies:
            w.body = i
            w.assure_newline() # instance method under test
            r = w.current_whitespace
            self.assertEqual(r, o, "Mismatch for input %r, expected %r but got %r" % (i, o, r))

    def test_assure_newlbock(self):
        class Doc(object):
            settings = None
        w = rst.RstTranslator(Doc())

        # XXX: not stripping/collapsing trailing ws, read source
        bodies = [
            ([' '], ' \n\n'),
            (['test test test '], ' \n\n'),
            (['test\t',' ','test '], ' \n\n'),
            ([' ','\ttest', '\n', ' ', '\t\n'], '\n \t\n'),
            ([' ','\ttest', ' \r\n', '', '\t   ','\t\n'], ' \r\n\t   \t\n'),
            (['  test  '], '  \n\n'),
        ]
        for i, o in bodies:
            w.body = i
            w.assure_newblock() # instance method under test
            r = w.current_whitespace
            self.assertEqual(r, o, "Mismatch for input %r, expected %r but got %r" % (i, o, r))
