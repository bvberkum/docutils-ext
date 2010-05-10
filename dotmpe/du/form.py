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
import logging
from docutils import nodes, utils
from dotmpe.du.ext import extractor
from dotmpe.du import util


logger = logging.getLogger(__name__)


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
                'default': 'name'}
        ),(
            'Alter the class-name that indicates form constructs.  ',
            ['--form-class'],
            {'action':'store_true', 'default': 'form'}
        ),(
            'Ignore any but explicitly listed names.  ',
            ['--form-fields'],
            {'action':'append', 'default': []}
        ),
        # --form-spec
    )

    def __init__(self, document, form_spec):
        self.document = document
        self.values = {}
        self.fields = {}
        self.nodes = {}
        self.fields.update([
            (field_id, FormField(field_id, *spec))
            for field_id, spec in form_spec.items() ])

    def process_fields(self):
        " Gather fields and convert data.  "
        fv = FormFieldIDVisitor(self.document)
        fv.initialize(self.fields.keys())
        fv.apply()
        seen = []
        for field_id, node in fv.form.items():
            # Get value. Errors are reported in document
            v = self.__process_field(field_id, node)
            self.values[field_id] = v
            if field_id not in seen:
                seen.append(field_id)
            self.nodes[field_id] = node
        if len(self.fields) > len(seen):
            # Report missing fields
            field_ids = self.fields.keys()
            [field_ids.remove(field_id) for field_id in seen]
            self.__report_missing(field_ids)

    def validate(self):
        " Validate form fields. "
        pass

    def __process_field(self, field_id, node, value=None):
        field = self.fields[field_id]
        name = extract_form_field_label(node)
        label, body = node[0], node[1]
        if len(node)>2:
            logger.info("Node contents out of bound for field %r. ", name)
        if field_id not in self.fields or not field.convertor:
            self.__report(node, UnknownFieldError, name)
        if value and not field.append:
            self.__report(node, DuplicateFieldError, name)
        data = None
        try:
            conv = field.convertor
            if not callable(conv):
                if len(conv)==2:
                    data = list(util.parse_list(body[0], *conv))
                elif len(conv)==3:
                    data = list(util.parse_nested_list(body[0], *conv))
                elif len(conv)==4:
                    data = list(util.parse_nested_list_with_headers(body[0], *conv))
            elif len(body):
                data = conv(body[0])
            else:
                data = u''
        except ValueError, e:
            self.__report(node, FieldValueError, name, e )
        except TypeError, e:
            self.__report(node, FieldTypeError, name, e )
        if field.append:
            if not value:
                value = []
            if isinstance(data, list):
                value.extend(data)
            else:
                value.append(data)
        else:
            value = data
        return value

    def __report_missing(self, field_ids):
        for field_id in field_ids:
            if self.fields[field_id].required:
                self.__report(None, MissingFieldError, field_id,)

    def __report_warning(self, node, error, *args):
        pass
    def __report_error(self, node, error, *args):
        msg = str(error(*args))
        self.document.reporter.error(msg, node) 


class FormField:

    def __init__(self, field_id, convertor, required=True, append=False, editable=True,
            disabled=False, validators=(), **classnames):
        self.field_id = field_id
        self.convertor = convertor
        self.required = required
        self.append = append
        self.editable = editable
        self.disabled = disabled
        self.validators = validators
        self.classnames = classnames


def extract_form_field_label(field):
    return field[0].astext().lower()


class AbstractFormVisitor(nodes.SparseNodeVisitor):

    def __init__(self, document):
        nodes.SparseNodeVisitor.__init__(self, document)
        self.settings = self.document.settings

    def apply(self):
        self.initialize()
        if self.settings.form != 'off':
            assert self.settings.form == 'name',\
                    "Unimplemented: %s" % self.settings.form
            self.document.walkabout(self)

    def initialize(self, field_ids=[]):
        if not hasattr(self, 'field_ids') or field_ids:
            self.field_ids = field_ids
        self.form = {} # name: field
        # TODO: self.fieldsets = []
        self.fieldset_class = self.settings.form_class
        self.field_class = self.fieldset_class + '-field'

    def is_fieldset(self, node):
        if self.__hasclass(node, self.fieldset_class):
            return True

    def is_field(self, field_node):
        if self.__hasclass(field_node, self.field_class):
            return True
        elif self.__hasfieldid(field_node):
            return True

    def scan_field(self, node):
        field_id = nodes.make_id(extract_form_field_label(node))
        if field_id in self.form:
            if not isinstance(self.form[field_id], types.ListType):
                self.form[field_id] = [self.form[field_id]]
            self.form[field_id].append(node)
        else:
            self.form[field_id] = node

        if self.field_class not in node['classes']:
            node['classes'].append(self.field_class)

    # util
    def _path(self, n):
        p = []
        p.insert(0, n.tagname)
        while hasattr(n, 'parent'):
            n = n.parent
            if not n: break
            p.insert(0, n.tagname)
        return '/'.join(p)

    def __hasclass(self, node, classname):
        if 'class' in self.settings.form:
            if classname in node:
                return True

    def __hasfieldid(self, node):
        if 'name' in self.settings.form:
            name = extract_form_field_label(node)
            field_id = nodes.make_id(name)
            return field_id in self.field_ids


class FormFieldSetVisitor(AbstractFormVisitor):
    def visit_definition_list(self, node):
        if self.is_form_element(node):
            pass # subs_add_form_class(node)

    def visit_field_list(self, node):
        if self.is_form_element(node):
            pass # subs_add_form_class(node)


class FormFieldIDVisitor(AbstractFormVisitor):

    # NodeVisitor hooks

    def visit_section(self, node):
        assert isinstance(node[0], nodes.title)
        if self.is_field(node):
            self.scan_field(node)

    def visit_definition_list_item(self, node):
        assert len(node.children) == 2
        if self.is_field(node):
            self.scan_field(node)

    def visit_field(self, node):
        assert len(node.children) == 2
        if self.is_field(node):
            self.scan_field(node)


## FormErrors


class FormError(utils.ExtensionOptionError): pass

class UnknownFieldError(FormError):
    def __str__(self):
        return "unknown option `%s`. " % self.args

class DuplicateFieldError(utils.DuplicateOptionError):
    def __str__(self):
        return "duplicate option `%s`. " % self.args

class FieldTypeError(utils.BadOptionDataError):
    def __str__(self):
        name, data, e = self.args
        return "invalid value type '%s' for option `%s`:\n\n\t%s " % (
                data, name, e)

class FieldValueError(utils.BadOptionDataError):
    def __str__(self):
        name, data, e = self.args
        return "invalid value '%s' for option `%s`:\n\n\t%s " % (
                data, name, e)

class MissingFieldError(FormError):
    def __str__(self):
        return "missing option `%s`. " % self.args


