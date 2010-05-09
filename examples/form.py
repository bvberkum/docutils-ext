"""
Work in progess example of form validation in docutils.

Lots to be desired:
  - more optionparser like functionality, such as help.
  - many unsupported constructs, ideas. What about feedback from output format, 
    e.g. HTML form.

Started:
  - spec second item indicates required, true when absent 
  - spec third item indicates append/concat multiple, false when absent
  - spec first item indicates validator, 2 validators for list parser,
    3 for tree or nested list parser, and 4 for a variant on nested lists..
  - various types of list parsing is supported
  - some ideas from docutils, examples below
  - errors are reported

XXX:BVB:I'm a little fuzzy on the last one or two convertors.
"""
import sys, os
from pprint import pprint
example_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.realpath(os.path.join(example_dir, '..', 'lib')))
from dotmpe.du import builder, util, form
from dotmpe.du.ext.transform import form1
from dotmpe.du.ext.extractor import form2
# this has some handy argument handlers
from docutils import readers, core, Component
from docutils.parsers.rst import directives


def color(node):
    return directives.choice(node.astext(),
            ['red','orange','yellow','green','blue','violet'])


# Extact the following fields from the document
# and demonstrate some argument parsers
# Note that all these fields need to be present.
def validate_myform(frmextr, settings):
    if 'my-exclusive-flag' in settings:
        assert 'my-flag' not in settings, "Cannot have both values. "
    return settings


# Reader with transform, and Builder with extractor configuration:

class FormReader(readers.Reader):

    settings_spec = (
        'My form', 
        None,
        form.FormProcessor.settings_spec + (
            ('',['--builder'],{}),
    ))

    extractors = [
            (form2.FormExtractor, form2.FormStorage),
        ]

    def get_transforms(self):
        return Component.get_transforms(self) + [
                form1.DuForm ]

class MyFormPage(builder.Builder):

    Reader = FormReader

    settings_overrides = {
        'form_spec': {
            'my-integer': (util.du_int,),
            'my-string': (util.du_str,),
            'my-yesno': (util.yesno,),
            'my-flag': (util.du_flag, False),
            'my-exclusive-flag': (util.du_flag, False),
            'my-colour': (color, False),
            #'my-uri': (util.du_uri,),
            #'my-integer-percentage': (util.percentage,),
            #'my-unsigned-integer': (util.nonnegative_int, False),
            'my-cs-list': ((util.cs_list, util.du_str), False, True),
            'my-ws-list': ((util.ws_list, int), False, True),
            'my-du-list': ((util.du_list, util.du_str), False, True),
            'my-du-tree': ((util.du_list, util.is_du_list, util.du_str), False, True),
            'my-du-tree-2': ((util.du_list, util.is_du_headed_list,
                util.du_nested_list_header, util.du_str), False, True),
        },
        'form': 'name',
    }


def reader_(source, source_id):
    doc = core.publish_string(source, source_id, 
            settings_overrides=MyFormPage.settings_overrides,
            reader=FormReader(), writer_name='pseudoxml')
    return doc


def builder_(source, source_id):
    builder = MyFormPage()
    builder.initialize(strip_comments=True)
    #print "Building %s" % source_id
    # Build the document tree from source
    document = builder.build(source, source_id)
    print document.settings.form_values
    
    return
    #print document.settings
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


if __name__ == '__main__':
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
        source_id = os.path.join(example_dir, 'form.rst')
    print 'Source:',source_id        
    source = open(source_id).read()

    if 'builder' in opts:
        builder_(source, source_id)
    else:
        print reader_(source, source_id)

