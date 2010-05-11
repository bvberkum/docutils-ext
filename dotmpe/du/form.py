"""
It may be convenient to treat a Du document as a form for user data. The
objective here is to extract and validate, and to feedback any errors.

Du Forms
==========
The result of the form is a set of key, value pairs. 
The following Du structures lend themselves for such model:

- field lists: name, body
- definition lists: term, definition
- sections: heading, body

To process these fields, the structure `FormField` is initialized for each 
`--form-field` [*]_. Processing consists of a conversion of the document node to 
primitive or complex data. 

TODO: validate and error report.

.. [#] The field's ID is created from the text in each 'label'. 
   XXX: Suboptimal.

This data is also kept on the settings object. This means validation may be 
requested upon extraction (form2) while the initial initialization is done 
during read or preparation of the document using the normal transform (form1).
XXX: eventually I think there should be some supporting Du/nodes form constructs.

ext.transform.form1.DuForm
    Process and validate according to settings. 

ext.transform.form1.GenerateForm
    Transform a document with form settings to include field structures for
    every or all required fields. May be used on empty or existing document.

ext.extractor.form2.FormExtractor and FormStorage
    Process/validate if needed (just like from1), and apply data per document to datastore.

ext.writer.xhtmlform
    Write Du documents with form constructs to XHTML, possibly validate.


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

Field types
------------


"""
import logging
from docutils import nodes, utils, transforms
from dotmpe.du.ext import extractor
from dotmpe.du import util


logger = logging.getLogger(__name__)

class FormProcessor:

    """
    Uses FormVisitor to fetch any form constructs from the document according to
    settings, and can process and validate the result data. Fields may be
    defined in the document's settings, see `--form-field` and 
    `FormProcessor.initialize(document)`.

    Fields should preferebly be specified using a subclass,

    """

    settings_spec = (
        (
            'Set form-recognition heuristics (see form documentation). '
            "(partial implementation, only 'off' and 'name' are working)",
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
            {'action':'append', 'default': [], 'metavar':'[ID[,ID]]'}
        ),(
            'Add or redefine a form-field (see form documentation). ',
            ['--field-spec', '--form-fields-spec'],
            { 'dest':'form_fields_spec', 'default':[], 'metavar':
                'id[,help];type[,require[,append[,editable[,disabled]]]][;vldtors,]', 
                'action':'append', 'validator': util.opt_form_field_spec, }
        )
    )

    fields_spec = []

    def __init__(self, document=None):
        self.document = None
        if document:
            self.initialize(document)

    def initialize(self, document, specs=None):
        """ Move processor to a new document. 
        Initialize form fields from settings if needed.  """
        if self.document:
            self.document.form_processor = None
        self.document = document
        self.__init_form_messages() # TODO: define some method for not adding
        #multiple sections
        settings = self.document.settings
        specs = specs or getattr(settings, 'form_fields_spec', [])
        self.fields = {} # field-id: Field
        self.__init_fields(specs)
        self.values = {} # field-id: value
        self.nodes = {} # field-id: node
        setattr(settings, 'form_values', self.values) # as dict or listed?
        setattr(document, 'form_processor', self)

    def __init_fields(self, specs):        
        for spec in specs:
            if not isinstance(spec, FormField):
                field_id, conv = spec[0:2]
                if len(spec)==3: attrs = spec[2]
                else: attrs = {}                    
                args, kwds = form_field_spec(field_id, conv, **attrs)
                spec = FormField(*args, **kwds)
            else:
                field_id = spec.field_id
            self.fields[field_id] = spec
                            

    def __init_form_messages(self):
        " Create a section in the document to keep messages.  "
        self.messages = nodes.section()
        self.messages.append(nodes.title('','Form Processor Messages'))
        # XXX: defer or configure; what if a site keeps it in some notice block
        self.document.append(self.messages)

    def process_fields(self):
        """
        Gather fields according to form-class or field-names, and convert data.
        Report datatype or value conversion errors but not form-errors.
        """
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
        # move this to validate?
        if len(self.fields) > len(seen):
            # Report missing fields
            field_ids = self.fields.keys()
            [field_ids.remove(field_id) for field_id in seen]
            self.__report_missing(field_ids)

    def validate(self):
        """
        Validate form fields, respecting properties and validators from 
        field-spec. """
        for fid, field in self.fields.items():
            if fid not in self.values:
                continue
            data = self.values[fid]
            for vldtor in field.validators:
                vldtor(data)

    def __process_field(self, field_id, node, value=None):
        field = self.fields[field_id]
        name = extract_form_field_label(node)
        label, body = node[0], node[1]
        if len(node)>2:
            logger.info("Node contents out of bound for field %r. ", name)
            # TODO: insert message at end-bound
        if field_id not in self.fields or not field.convertor:
            self.__report_error(node, UnknownFieldError, name)
        if value and not field.append:
            self.__report_error(node, DuplicateFieldError, name)
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
            self.__report_error(node, FieldValueError, body, name, e )
        except TypeError, e:
            self.__report_error(node, FieldTypeError, body, name, e )
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
                self.__report(3, None, MissingFieldError, field_id,)
            else:
                self.__report(1, None, MissingFieldNotice, field_id,)

    def __report(self, level, node, error, *args):
        msg = str(error(*args))
        sysmsg = self.document.reporter.system_message
        if node:
            msgnode = sysmsg(level, msg, node) 
        else:
            msgnode = sysmsg(level, msg)
        self.messages.append(msgnode)            
        return msgnode

    def __report_error(self, *args):
        return self.__report(3, *args)


def extract_form_field_label(field):
    " Return text-value of first node.  "
    return field[0].astext()


class FormField:

    """
    Struct for keeping metadata for form fields. Prolly should move some into
    DOM?
    """

    def __init__(self, field_id, convertor, required=True, append=False, 
            editable=True, disabled=False, validators=(), help=''):
        self.field_id = field_id
        self.convertor = convertor
        self.required = required
        self.append = append
        self.editable = editable
        self.disabled = disabled
        self.validators = validators
        self.help = help


def form_field_spec(field_id, convertor_or_names, **attrs): 
    " Preprocess FormField spec, resolve convertor names. "
    if not callable(convertor_or_names):
        conv = util.get_convertor(convertor_or_names)
    else:
        conv = convertor_or_names
    return (field_id, conv), attrs


# Du document visitors

class AbstractFormVisitor(nodes.SparseNodeVisitor):

    def __init__(self, document):
        nodes.SparseNodeVisitor.__init__(self, document)
        self.settings = self.document.settings

    def apply(self):
        self.initialize()
        if getattr(self.settings, 'form', 'off') != 'off':
            # XXX: fieldset and class-directive scan not implemented
            assert self.settings.form == 'name',\
                    "Unimplemented: %s" % self.settings.form
            self.document.walkabout(self)

    def initialize(self, field_ids=[]):
        """ Initialize or reset field-id list.  """
        if not hasattr(self, 'field_ids') or field_ids:
            self.field_ids = field_ids
        self.form = {} # field-id: du-node
        self.fieldset_class = getattr(self.settings, 'form_class', 'form')
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
        return "unknown or disallowed field `%s`. " % self.args

class DuplicateFieldError(utils.DuplicateOptionError):
    def __str__(self):
        return "duplicate field `%s`" % self.args

class FieldTypeError(utils.BadOptionDataError):
    def __str__(self):
        name, data, e = self.args
        return "invalid value type '%s' for field `%s`:\n\n\t%s " % (
                data, name, e)

class FieldValueError(utils.BadOptionDataError):
    def __str__(self):
        name, data, e = self.args
        return "invalid value '%s' for field `%s`:\n\n\t%s" % (
                data, name, e)

class MissingFieldError(FormError):
    def __str__(self):
        return "missing required field `%s`" % self.args

class MissingFieldNotice(FormError):
    def __str__(self):
        return "field `%s` also available " % self.args


