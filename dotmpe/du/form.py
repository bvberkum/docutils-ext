"""
It may be convenient to treat a Du document as a form for user data. The
objective here is to extract, validate, and to feedback processing errors as
system-messages.

ext.transform.form.DuForm
    Heuristics to find form fields, attach to definition.
    Validate entries, reports problems in-tree.

ext.transform.form.FormTransform
    Transform a Form values object into a Du document.

ext.extractor.form.FormExtractor and FormStorage
    Apply validated entries to datastore.

ext.writer.html4css1form
    Write Du documents with form constructs to XHTML, possibly validate.


Du Forms
==========
A form is defined as any set of key, value pairs. Nested in sets with a key
if needed.

The following Du structures lend themselves for such model:

- field lists: name, body
- definition lists: term, definition
- sections: heading, body

Note: Nesting needs special considerations for validation. 

Besides converting the whole tree to a form in such a fashion, it may be more
effective to divide some options for recognizing forms:

- by 'form' class
- by section-title/definition-term/field-name or path (in case of nesting)
- by options listed explicitly in document

This proposal does not introduce its own directives or nodes?
A directive might be, but I've observed discussions on rSt where the concensus
was that if a generic construct can do the job of a more specific one, then the
former is preferred. Ie. the option-list would have been deprecated if e.g.
definition list could capture the same.

Validation
----------
- Any list of parametrized validators per primitive type.
- An additional special validator for lists.
- Two additional for trees (branching lists).

"""
from docutils import nodes, DataError
from dotmpe.du.ext import extractor
from dotmpe.du import util


class FormData:

    def asxml(self): pass
    def astags(self): pass
    def asdom(self): pass

    @classmethod
    def fromxml(clss):pass
    def fromdom():pass
    def fromtags():pass


class FormProcessor:

    """
    Uses FormVisitor to fetch any form constructs from the document according to
    settings, and process and validate the result values according to form_spec.

    form_spec should preferebly be specified using a subclass.

    Use the option_spec to specify which fields to extract and with what
    convertor and validators.
    """

    settings_spec = (
        (
            'Set form-recognition heuristics (see form documentation). ',
            ['--form'], 
            {'choices':['off', 'class', 'name', 'class-and-name'], 
                'default': 'class-and-name'}
        ),(
            'Alter the class-name that indicates form constructs.  ',
            ['--form-class'], 
            {'action':'store_true', 'default': 'form'}
        ),(
            'Ignore any but explicitly listed names.  ',
            ['--form-fields'], 
            {'action':'append', 'default': []}
    ))

    def __init__(self, document, fields_specs):
        self.document = document
        self.settings = document.settings
        self.fields = {}
        self.fields.update([(field_id,{'spec':spec})
            for field_id, spec in fields_specs.items()])

    def process_fields(self):
        fv = FormVisitor(self.document)
        fv.apply()
        self.extract_fields(fv.form)

    def extract_fields(self, fields):
        print 'ef', fields
        #extract_form_fields(fields, 
        values = {}

    def validate(self):
        pass
    

def extract_form_name(field):    
    return field[0].astext().lower()

def extract_form_fields(fields, options_spec, raise_fail=True, errors=[]):
    pass


class FormVisitor(nodes.SparseNodeVisitor):

    """
    Scan tree for section, field or definition_list_item that qualify as form-field
    or field-set.
    """

    def __init__(self, document):
        nodes.SparseNodeVisitor.__init__(self, document)
        self.settings = self.document.settings

    def apply(self):
        self.initialize()
        if self.settings.form != 'off':
            self.document.walkabout(self)

    def initialize(self):
        self.form = {} # name: field
        # TODO: self.fieldsets = []

    def readable_field(self, node):
        if 'class' in self.settings.form:
            # XXX: what about superstructure, cascade class down?
            return self.settings.form_class in node
        if 'name' in self.settings.form:
            name = extract_form_name(node)
            return name in self.settings.form_fields

    # pseudo hook
    def visit_form(self, node):
        if not self.readable_field(node):
            return
        name = extract_form_name(node)
        if name in self.form:
            if not isinstance(self.form[name], types.ListType):
                self.form[name] = [self.form[name]]
            self.form[name].append(node)
        else:
            self.form[name] = node

    # NodeVisitor hooks
    def visit_section(self, node):
        assert isinstance(node[0], nodes.title)
        self.visit_form(node)

    def visit_definition_list_item(self, node):
        assert len(node.children) == 2
        self.visit_form(node)

    def visit_field(self, node):
        assert len(node.children) == 2
        self.visit_form(node)


