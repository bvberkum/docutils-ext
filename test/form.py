"""
Form unittest and extractor (use nabu-test-extractor).
"""
import unittest
import sys, os
import optparse
from pprint import pprint
test_dir = os.path.dirname(__file__)
example_dir = os.path.realpath(os.path.join(test_dir, '..', 'examples'))
sys.path.insert(0, os.path.realpath(os.path.join(example_dir, '..', 'lib')))
import dotmpe.du
from dotmpe.du import builder, util, form
from dotmpe.du.ext.transform import form1
from dotmpe.du.ext.extractor import form2
# this has some handy argument handlers
from docutils import readers, core, Component
from docutils.parsers.rst import directives


def color(node):
    return directives.choice(node.astext(),
            ['red','orange','yellow','green','blue','violet'])

util.data_convertor['color'] = color

def validate_myform(frmextr, settings):
    if 'my-exclusive-flag' in settings:
        assert 'my-flag' not in settings, "Cannot have both values. "
    return settings


class Form:

    fields_spec = [
        ('my-integer','int',),
        ('my-string', 'str',),
        ('my-bool','bool',),
        ('my-yesno','yesno',),
        ('my-flag','flag',{ 'required': False }),
        ('my-exclusive-flag','flag',{ 'required': False }),
        ('my-colour','color',{ 'required': False }),
        #('my-uri': (util.du_uri,),
        #('my-integer-percentage': (util.percentage,),
        ('my-unsigned-integer','int',{ 'required':False,
            'validators':(lambda i:i>=0,), 'help': 'Enter a non-negative integer. ' }),
        ('my-cs-list','cs-list,str',{ 'required':False, 'append':True }),
        #(util.cs_list, util.du_str)
        ('my-ws-list','ws-list,int',{ 'required':False, 'append':True }),
        #(util.ws_list, int)
        ('my-du-list','list,str',{ 'required':False, 'append':True }),
        #(util.du_list, util.du_str)
        ('my-du-tree','tree1,str',{ 'required':False, 'append':True }),
        #(util.du_list, util.is_du_list, util.du_str)
        ('my-du-tree-2','tree2,str',{ 'required':False, 'append':True }),
        #(util.du_list, util.is_du_headed_list, util.du_nested_list_header, util.du_str)
    ]

class FormExtractor(form2.FormExtractor):
    fields_spec = Form.fields_spec
class FormTransform(form1.DuForm):
    fields_spec = Form.fields_spec

class FormReader(readers.Reader):

    settings_spec = (
        'My form',
        None,
        form.FormProcessor.settings_spec + (
    ))

    extractors = [
            (FormExtractor, form2.FormStorage),
        ]

    def get_transforms(self):
        return Component.get_transforms(self) + [
                FormTransform ]


from StringIO import StringIO
warnings = StringIO()

class MyFormPage(builder.Builder):

    Reader = FormReader

    settings_overrides = {
        'warning_stream': warnings
    }


def reader_(source, source_id):
    doc = core.publish_string(source, source_id,
            settings_overrides=MyFormPage.settings_overrides,
            reader=FormReader(), writer_name='pseudoxml')
    return doc

def builder_(source, source_id):
    builder = MyFormPage()
    builder.prepare_initial_components()
    builder.prepare()
    #assert builder.reader.extractors
    #builder.initialize(strip_comments=True)
    print "Building %s" % source_id
    # Build the document tree from source
    document = builder.build(source, source_id)
    assert builder.extractors
    builder.process(document, source_id)
    print document.settings.form_values
    return
    #print "Processing"
    # Extract form data
    builder.prepare()
    builder.process(document, source_id)
    # SimpleFormStorage kept the values for each document it processed:
    #print "Settings:"
    #pprint(builder.extractors[0][1].form_settings)
    # Print reports
    if builder.build_warnings.tell():
        print >>sys.stderr, "Build messages:\n%s\n"\
                "There where messages during building.\n" %\
                builder.build_warnings.getvalue()
    if builder.process_messages:
        print >>sys.stderr, "Process messages:\n%s\n"\
            "There where errors during processing. " %\
            builder.process_messages

def main_():
    args = sys.argv[1:]
    opts = {}
    source_id = None
    while args:
        arg = args.pop()
        if arg.startswith('-'):
            opts[arg.lstrip('-')] = None
        else:
            source_id = arg
    if not source_id:
        source_id = os.path.join(example_dir, 'form-1.rst')
    print 'Source:',source_id
    source = open(source_id).read()

    if 'builder' in opts:
        builder_(source, source_id)
    else:
        print reader_(source, source_id)


# see example/form.rst
expected = {
        'my-cs-list': [u'1', u'two', u'3', u'and four'],
        'my-ws-list': [1, 2, 3],
        'my-du-list': [u'1', u'2'],
        'my-du-tree': [[u'nesting test 1.1', u'test 1.2'], [u'2.1', u'2.2', [[u'2.3.1.1']]], u'3', [u'4.1', [[[[[u'4.2.1.1.1.1.1']]]], u'4.2.2', u'4.2.3']]],
        'my-du-tree-2': [[u'branch 1', [[u'branch 1.1', [u'leaf 1.1.1', u'leaf 1.1.2']], u'leaf 1.2', u'leaf 1.3']], u'branch 2', [u'branch 3', [u'leaf 3.1', u'leaf 3.2']]],
        'my-string': 'test',
        'my-integer': 123,
        'my-yesno': True,
        'my-colour': 'red',
        'my-flag': u'',
        'my-exclusive-flag': u'',
        'my-error': u'',
    }

# Main test: one test
class FormTest(unittest.TestCase):

    def test_1(self):
        source_id = os.path.join(example_dir, 'form-1.rst')
        source = open(source_id).read()
        builder = MyFormPage()
        #builder.initialize(strip_comments=True)
        document = builder.build(source, source_id)
        assert isinstance(document.settings, optparse.Values),\
                repr(document.settings)
        form_values = getattr(document.settings, 'form_values', ())
        for field_id, value in form_values:
            self.asertEquals(expected[field_id], value, "Value error for %s: %r" % (field_id, value))

    def test_2(self):
        pass


if __name__ == '__main__':
    if sys.argv:
        main_()
    else:
        unittest.main()
