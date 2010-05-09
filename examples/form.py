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
from dotmpe.du.ext.extractor import form2
# this has some handy argument handlers
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


class MyFormPage(builder.Builder):

    settings_spec = (
            '', None,
            form.FormProcessor.settings_spec
        )

    class FormExtractor(form2.FormExtractor):
        options_spec = {
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
            }
        
    extractors = [
            (FormExtractor, form2.FormStorage),
        ]


# Simple command-line processing
if sys.argv[1:]:
    source_id = sys.argv[1]
else:
    source_id = os.path.join(example_dir, 'form.rst')
source = open(source_id).read()
builder = MyFormPage()
builder.initialize(strip_comments=True)
print builder.overrides

print "Building %s" % source_id

# Build the document tree from source
document = builder.build(source, source_id)

print "Processing"

# Extract form data
print builder.settings_spec
builder.prepare()
builder.process(document, source_id)

# SimpleFormStorage kept the values for each document it processed:
print "Settings:"
pprint(builder.extractors[0][1].form_settings)

# Report error
if builder.build_warnings:
    print >>sys.stderr, "Build messages:"
    print >>sys.stderr, builder.build_warnings
    print >>sys.stderr, "There where messages during building. "
    print >>sys.stderr

if builder.process_messages:
    print >>sys.stderr, "Process messages:"
    print >>sys.stderr, builder.process_messages
    print >>sys.stderr, "There where errors during processing. "
    print >>sys.stderr


