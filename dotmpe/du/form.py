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

Note each of these structures can nest itself, and ofcourse rSt marked-up
content. The initial version processes fields which text's mkid matches to 
a fieldspec.

To process fields, structure `FormField` is initialized for each given spec.
Specs are passed programmatically or using `--form-field`. 

Processing then consists of a conversion of the document node to
primitive or complex data. Some basic types are implemented.

When validation is done, the settings key 'validated' is set to true, so care
must be taken by any calling code to properly match this status to a specific
set of fields. 

Most interaction is programmatically to the FormProcessor instance, which is
put on the document and vice versa, and which holds extracted values.


ext.transform.form1.DuForm
    A standard Du transform, processes and validate according to settings or its
    own fields_spec.

ext.transform.form1.GenerateForm
    Transforms a document with form settings to include field structures
    (nodes) for every or all required fields. May be used on empty or
    existing document.

ext.extractor.form2.FormExtractor and FormStorage
    No more processing or validation, if valid apply data to storage.

    Process/validate if needed (just like from1), and apply data per document to datastore.

ext.writer.xhtmlform
    Write Du documents with form constructs to XHTML, possibly validate.


Besides converting the whole tree to a form, it may be more
effective to divide some options for recognizing forms:

- by 'form' class
- by section-title/definition-term/field-name or path (in case of nesting)
- by options listed explicitly in document

This proposal does not introduce its own directives or nodes?

.. 
    A directive might be, but I've observed discussions on rSt where the concensus
    was that if a generic construct can do the job of a more specific one, then the
    former is preferred. Ie. the option-list would have been deprecated if e.g.
    definition list could capture the same.

..
    FormFieldIDVisitor is not going to help extracting data from patterns in
    nesting.

Field types
------------
- str, whitespace collapsed unicode
- text, multiline unicode
- href, a 'valid' URI or hyper-reference
- reference, str with href
- email, str with mailto: href
- list, combined with anyther field-type
- bool, any on of the str's '0', '1', 'True', 'False', 'On', 'Off', 'true', etc.

Field specification
-------------------
::
        '<field-id>', '<field-type>', <attr>

The attr is an optional dict that makes the spec extensible for all sorts of
types and some features. Implemented::

    required
        Boolean
    append
        Makes field spec multi-matching. TODO: figure out some way around unique
        IDs and maybe names then.

XXX: Should match fields to proper id/name during parse or read. Requires some DB indices.
TODO: Get some tab/csv ouput writer going.
TODO: Scanning and denormalization of nested fields into rows for output.
"""
import logging, types
from docutils import nodes, utils, transforms
from docutils.frontend import Values
from dotmpe.du.ext import extractor
from dotmpe.du import util


logger = util.get_log(__name__)


def opt_form_prepare():
    pass

class FormProcessor:

    """
    Uses FormVisitor to fetch any form constructs from the document according to
    settings, and can process and validate the result data. Fields may be defined
    in the document's settings (using the 'form_fields_spec', see `--field-spec`)
    or added the programmatic way by initializing the FormProcessor manually.

    Instances of this class are attached to the form_processor attribute on the
    document, and initialized/reused by the 3 form transformations, which to the
    actual processing on the document.

    - form1.GenerateForm may be run first to add missing fields, optional or otherwise.
    - form1.DuForm may be used (e.g. on a custom Du Reader),
      to initialize the form for a certain fields_spec or to validate the form.
    - form2.FormExtractor is applied by Builder.process and may do the same as
      GenerateForm (if not done yet), and also submit the values to storage, if
      valid.

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
            {'action':'store', 'default': 'form'}
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
        ),(
            "Set 'prepare' for pass-through of current field entries, or "
            "'submit' to store (after validation). The default 'validate' "
            "reports all field-data conversion and validation errors. ",
            ['--form-process'],
            { 'choices':['prepare','validate','submit'],'default':'validate' }
            # TODO: 'validator':
        ),(
            'Form field generator policy. See form documentation. ',
            ['--form-generate'],
            { 'choices':['off','all','optional','required','editable','noneditable'],
                'default':'required+noneditable'}
            #'validator': util., }
        )
    )

    fields_spec = []

    def __init__(self, document=None):
        self.document = None
        if document:
            self.initialize(document)

    def initialize(self, document, fields_spec=[]):
        """ Move processor to a new document.
        Initialize form fields from settings if needed.  """
        if self.document:
            self.document.form_processor = None # move on to next doc
        self.document = document
        settings = self.document.settings
        if not hasattr(settings, 'validated'):
            settings.validated = False
        self.settings = settings
        self.messages = []
        self.errors = []
        #setattr(document, 'form_messages', self.messages)
        specs = self.fields_spec or fields_spec or getattr(settings,
                'form_fields_spec', [])
        self.fields = {} # field-id: Field
        self.__init_fields(specs)
        self.values = {} # cache for get-item, field-id: value
        #setattr(settings, 'form_values', self.values) # as dict or listed?
        self.nodes = {} # field-id: node
        self.invalid = {}
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
        # XXX: Use system-messages section, but there is no default way, like
        # decorator, to retrieve that section
        sysmsgsclass = 'system-messages'
        doc = self.document
        for idx in range(len(doc)-1, 0, -1):
            if isinstance(doc[idx], nodes.section) and sysmsgsclass in doc[idx]:
                self.messages = document[idx]
                return
        self.messages = nodes.section(classes=[sysmsgsclass])
        self.messages += nodes.title('', 'Docutils System Messages')
        doc += self.messages
        # XXX: defer or configure; what if a site keeps it in some notice block

    def process_fields(self, require_value=True):
        """
        Gather field nodes according to form-class or field-names. For each
        there may be a value, contained either in the 'body' of the node, or in
        the defaults. This method saves the node to self.nodes, and makes sure
        that its datatype validates. The value may be retrieved or set using
        self.values[field_id].

        Reports datatype or value conversion errors but not form-errors.
        """
        fv = FormFieldIDVisitor(self.document)
        fv.initialize(self.fields.keys())
        fv.apply()
        self.seen = []
        # iterate found fields
        for field_id, node in fv.fields:
            # keep list of nodes for 'append'-value setting
            if self.fields[field_id].append:
                if field_id not in self.nodes:
                    self.nodes[field_id] = []
                self.nodes[field_id].append(node)
            # or single occurrences
            elif field_id in self.nodes:
                self.__report_error(node, DuplicateFieldError, field_id)
                continue
            else:
                self.nodes[field_id] = node
            # track id
            if field_id not in self.seen:
                self.seen.append(field_id)
            # pre-cache node's value
            if require_value:
                try:
                    value = self[field_id]
                except KeyError, e:
                    assert False, "Unexpected missing node for field %s" % field_id
                    #self.__report_error(node, KeyError, e)
                except TypeError, e:
                    self.__report_error(node, TypeError, e)
                except ValueError, e:
                    self.__report_error(node, ValueError, field_id, '', e)
            #self.__report_missing(field_ids, require_value)

    def __nonzero__(self):
        return self.nodes != {}

    def __contains__(self, field_id):
        return field_id in self.nodes

    def __iter__(self):
        for field_id in self.nodes:
        	yield field_id

    def __getitem__(self, field_id):
        """Return cached value. """
        if field_id not in self.values:
            v = self.__process_field(field_id)
            if field_id=='id':
                logging.info("%s: %s", field_id, v)

            self.values[field_id] = v
        return self.values[field_id]

    def __setitem__(self, field_id, value):
        self.document.validated = False
        if isinstance(value, nodes.Element):
            #logger.debug('Inserted at %r raw node fragment: %r', field_id, value)
            self.nodes[field_id] = value # XXX: insert into doc..
            return
        if field_id not in self.nodes:
            #logger.info('Preparing node for %r', field_id)
            form_class = getattr(self.settings, 'form_class', 'form')
            fnode = nodes.field(classes=[form_class+'-field'])
            fnode += nodes.field_name(field_id, field_id),\
                nodes.field_body()
            self.nodes[field_id] = fnode
            # place/extend field-list in front of document.
            field_list = self.__insert_field_list(form_class)
            field_list += fnode
        self.__wrap_field(field_id, value)

    def validate(self):
        """
        Validate form fields, respecting properties and validators from
        field-spec.
        """
        logger.info('Validating %s', self.document['source'])
        v = not self.errors
        if not v:
            return v
        for fid, field in self.fields.items():
            if not field.editable or field.disabled:
                continue # XXX: oldval == newval
            if fid not in self:
                logging.info("MissingFieldNotice %s", fid)
                if field.required:
                    self.__report( 3, None, MissingFieldError, fid )
                    v = False
                continue
            data = []
            node = self.nodes.get(fid, None)
            if fid in self:
                try:
                    d = self[fid]
                    if isinstance(d, list):
                        data.extend(d)
                    else:
                        data = [d]
                except KeyError, e:
                    assert False, "fid is in self?"
                except TypeError, e:
                    self.__report_error(node, FieldTypeError, e)
                    self.invalid[fid] = value
                    v = False
                except ValueError, e:
                    self.__report_error(node, FieldValueError, fid, data, e)
                    self.invalid[fid] = value
                    v = False
            for value in data:
                if type(value) == type(None) and not field.required:
                    continue
                assert not fid in self.invalid, "Not implemented"
                for vldtor in field.validators:
                    try:
                        _v = vldtor(value, self)
                        logger.info("%s, %s, %s", vldtor, _v, v)
                        v = v and _v
                    except ValueError, e:
                        self.invalid[fid] = value
                        self.__report(3, node, FieldValueError, fid, data, e)
                        v = False
                        continue
                    except Exception, e:
                        import traceback, sys
                        traceback.print_exc(sys.stderr)
                        assert False, "Unexpected validation failure: %s" % e
                if type(value) == type(None) and field.required:
                    self.__report( 3, node, MissingFieldError, fid )
                    self.invalid[fid] = value
                    v = False
        self.document.settings.validated = v
        if v:
            # FIXME: multiple forms by index or name?
            values = dict([(k.replace('-','_'), v)
                for k, v in self.values.items() if type(v) != type(None)])
            setattr(self.document, 'form', values)
        else:
            assert self.invalid, "Invalid form but no invalid fields. "
            logger.info('Invalid document %s, fields: %s',
                    self.document['source'], self.invalid)
        return v

        # XXX: Old?
        if len(self.fields) > len(self.seen):
            # Report missing fields
            missing = self.fields.keys()
            [missing.remove(field_id) for field_id in self.seen]
            for field_id in missing:
                if self.fields[field_id].required:
                    v = False
                    self.__report(3, None, MissingFieldError, field_id,)
                else:#if report_optional:
                    self.__report(1, None, MissingFieldNotice, field_id,)

        return v

    def iter_missing(self, *generate):
        " Iterate Ids and fields for missing nodes. "
        generate = list(generate) or getattr(self.document.settings, 'form_generate',
                'required')
        if 'off' in generate:
            pass
        elif 'all' in generate:
            for field_id, field in self.fields.items():
                if field_id not in self.nodes:
                    yield field_id, field
        else:
            if not 'optional' in generate:
                if not 'required' in generate:
                    generate.append('required')
            editable = ('editable' in generate or 'noneditable' not in generate)
            required = ('required' in generate or 'optional' not in generate)
            for field_id, field in self.fields.items():
                if field_id not in self.nodes:
                    if field.required and required or \
                            field.editable and editable:
                        yield field_id, field

    def __insert_field_list(self, form_class):
        index = self.document.first_child_not_matching_class(
            nodes.PreBibliographic)
        if index:
            candidate = self.document[index]
            #logger.info('Candidate %s', candidate)
            if isinstance(candidate, nodes.field_list):
                return candidate
            elif isinstance(candidate, nodes.docinfo):
                index += 1
        else:
            index = 0
        field_list = nodes.field_list(classes=[form_class])
        if index:
            self.document.insert(index, field_list)
        else:
            self.document.append(field_list)
        return field_list

    def __wrap_field(self, field_id, value):
        node = self.nodes[field_id]
        label, body = node[0], node[1]
        #body.append(nodes.Text(value))
        body[:] = [nodes.paragraph('',nodes.Text(value))]
        #logger.debug("Filled in with %s for %r", value, field_id)

    def __process_field(self, field_id):
        """
        Extract value from node using field.
        """
        node = self.nodes[field_id]
        if isinstance(node, list):
            if len(node) == 1:
            	node = node[0]
        assert not isinstance(node, list), \
                "Multiple fields not supported (field %s, %s). " % (field_id, node)
        name = extract_form_field_label(node)
        field = self.fields[field_id]
        if field_id not in self.fields or not field.convertor:
            self.__report_error(node, UnknownFieldError, name)
        if len(node)>2:
            logger.info("Node contents out of bound for field %r. ", name)
            # TODO: insert message at end-bound
        label, body = node[0], node[1]
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
                data = conv(None)
        #except Exception, e:
        #    import traceback, sys
        #    traceback.print_exc(sys.stderr)
        #    raise
        except ValueError, e:
            self.__report_error(node, FieldValueError, name, body.astext(), e )
        except TypeError, e:
            self.__report_error(None, FieldTypeError, name, body.astext(),
                    conv.__name__, e )
            #finally:
            #    if isinstance(data, types.NoneType):
            #        data = u''
        value = None
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

    def __report(self, level, node, error, *args):
        msg = str(error(*args))
        sysmsg = self.document.reporter.system_message
        #if node:
        #    msgnode = sysmsg(level, msg, node)
        msgnode = sysmsg(level, msg)

        prbid = 'unknown'
        if node and len(node)>=2 and len(node[1]):
            node = node[1][0]
            msgid = self.document.set_id(msgnode)
            # XXX: include problematic/invalid values or not..
            prb = nodes.problematic('',node.astext(), refid=msgid)
            prbid = self.document.set_id(prb)
            msgnode.add_backref(prbid)
            node.replace_self(prb)
            #prb += node
        logger.info('Reported %s: %s, %s', level, error, prbid)

        self.messages.append(msgnode)
        return msgnode

    def __report_error(self, *args):
        return self.__report(3, *args)

    def __insert_data():
        pass

    @classmethod
    def get_instance(clss, document, fields_spec=[]):
        if not hasattr(document, 'form_processor'):
            logger.debug('Created new FormProcessor for %s',
                    document['source'])
            pfrm = FormProcessor(document)
        else:
            logger.debug('Reusing FormProcessor for %s',
                    document['source'])
            pfrm = document.form_processor
        pfrm.initialize(document, fields_spec=fields_spec)
        return pfrm


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
        "Callable to convert string argument to native type.  "
        self.required = required
        "Field must be present and will be validated, even if null-value.  "
        self.append = append
        "Multiple fields will be concatenated. "
        self.editable = editable
        "Process, but neither change nor validate field. "
        self.disabled = disabled
        "Same effect as editable, other semantics? "
        self.validators = validators
        "List of callables invoked with value and processor as arguments. "
        self.help = help
        "Generic help text for field entry. "


def form_field_spec(field_id, convertor_or_names, validators=(), **attrs):
    " Preprocess FormField spec, resolve convertor names. "
    vtors = []
    for vtorname in validators:
        if not callable(vtorname):
            vtor = util.validators[vtorname]
            if callable(vtor):
                vtors.append(vtor)
            else:# tuple
                vtors.extend(vtor)
    attrs['validators'] = vtors
    if not callable(convertor_or_names):
        conv = util.get_convertor(convertor_or_names)
    else:
        conv = convertor_or_names
    return (field_id, conv), attrs


# Du document visitors

class AbstractFormVisitor(nodes.SparseNodeVisitor):

    """
    Implements handling of the document.settings.form settings.
    """

    def __init__(self, document):
        nodes.SparseNodeVisitor.__init__(self, document)
        self.settings = self.document.settings

    def apply(self):
        self.initialize()
        if not hasattr(self.settings, 'form'):
            setattr(self.settings, 'form', 'name')
        if self.settings.form != 'off':
            # XXX: fieldset and class-directive scan not implemented
            assert self.settings.form == 'name',\
                    "Unimplemented: %s" % self.settings.form
            self.document.walkabout(self)

    def initialize(self, field_ids=[]):
        """ Initialize or reset field-id list.  """
        if not hasattr(self, 'field_ids') or field_ids:
            self.field_ids = field_ids
        self.fields = []
        "Captured fields"
        self.fieldset_class = getattr(self.settings, 'form_class', 'form')
        ""
        self.field_class = self.fieldset_class + '-field'
        ""

    def is_fieldset(self, node):
        if self.__hasclass(node, self.fieldset_class):
            return True

    def is_field(self, field_node):
        ""
        if self.__hasclass(field_node, self.field_class):
            return True
        elif self.__hasfieldid(field_node):
            return True

    def scan_field(self, node):
        """
        If the element matches as a field, capture it.
        """
        if self.settings.form == 'class' or self.settings.form == 'class-and-name':
        	pass
        if self.settings.form == 'name' or self.settings.form == 'class-and-name':
        	pass
        field_id = nodes.make_id(extract_form_field_label(node))
        if self.field_class not in node['classes']:
            node['classes'].append(self.field_class)
        self.fields.append((field_id, node))

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
        if self.is_fieldset(node):
            pass # subs_add_form_class(node)

    def visit_field_list(self, node):
        if self.is_fieldset(node):
            pass # subs_add_form_class(node)


class FormFieldIDVisitor(AbstractFormVisitor):

    """
    FieldID visitor matches various Du elements based on the mkid
    of their text contents.
    """

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

class UnknownFieldError(FormError, KeyError):
    def __str__(self):
        return "unknown or disallowed field `%s`" % self.args

class DuplicateFieldError(utils.DuplicateOptionError):
    def __str__(self):
        return "duplicate field not allowed for `%s`" % self.args

class FieldTypeError(utils.BadOptionDataError):
    def __str__(self):
        name, data, convtr, e = self.args
        return "convertor %r not applicable to '%s' for field `%s`:  %s" % (
                convtr, data, name, e)

class FieldValueError(utils.BadOptionDataError):
    def __str__(self):
        name, data, e = self.args
        if isinstance(data, list):
            return "invalid value in field `%s`: %s" % ( name, e )
        else:
            return "invalid value for field `%s`: %s" % ( name, e )

class MissingFieldError(FormError):
    def __str__(self):
        return "field `%s` is required" % self.args

class MissingFieldNotice(FormError):
    def __str__(self):
        return "field `%s` also available" % self.args


