"""
Work in progess example of form validation in docutils.

Lots to be desired:

- parse docutils tree structures like lists perhaps.
- more optionparser like functionality, such as help, required vs. optional,
  append.
- more sophisticated validator feedback by transforming doctree and inserting
  errors and messages.

"""
import sys, os
from pprint import pprint
example_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.realpath(os.path.join(example_dir, '..', 'lib')))
from dotmpe.du import builder, util
from dotmpe.du.ext.extractor import form
# this has some handy argument handlers
from docutils.parsers.rst import directives


def color(argument):
    return directives.choice(argument,
            ['red','orange','yellow','green','blue','violet'])


# Extact the following fields from the document
# and demonstrate some argument parsers
# Note that all these fields need to be present.
FormExtractor = form.FormExtractor
FormExtractor.option_spec = {
        'my-integer': int,
        'my-string': str,
        'my-yesno': util.yesno,
        'my-flag': directives.flag,
        'my-exclusive-flag': directives.flag,
        'my-colour': color, 
        'my-uri': directives.uri,
        'my-integer-percentage': directives.percentage,
        'my-unsigned-integer': directives.nonnegative_int,
        'my-list': util.cs_list,
    }
form_values = form.SimpleFormStorage()
def validate_myform(frmextr, settings):
    return settings
form_values.validate = validate_myform

class MyFormPage(builder.Builder):

    extractors = (
            (FormExtractor, form_values),
        )


# Simple command-line processing
if sys.argv[1:]:
    source_id = sys.argv[1]
else:
    source_id = os.path.join(example_dir, 'form.rst')
source = open(source_id).read()
builder = MyFormPage()

# Build the document tree from source
document = builder.build(source, source_id)
if builder.build_warnings:
    print >>sys.stderr, builder.build_warnings
    print >>sys.stderr, "Unable to build document %s. " % source_id
    sys.exit(1)

# Extract form data
builder.process(document, source_id)
if builder.process_messages:
    print >>sys.stderr, builder.process_messages
    print >>sys.stderr, "Unable to process form in %s." % source_id
    sys.exit(2)

# SimpleFormStorage kept the values for each document it processed:
pprint(form_values.document_settings)

