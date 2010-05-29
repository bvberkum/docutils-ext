"""
Helper functions.

Mainly convertors and validators, but needs some cleaning up.

- Convertors. Used as argument parsers on strings and doctree fragments to
  extract certain data types. May return None and raise Value or Type Errors.
- Validators. Used for option or form validation... XXX: raises validation error?

"""
import re
import uriref
from docutils import utils, nodes, frontend
#from docutils.nodes import fully_normalize_name, make_id
from dotmpe.du.ext.transform import include
from docutils.parsers.rst import directives



def new_document(source_path, settings=None):
    if settings is None:
        settings = frontend.OptionParser().get_default_values()
    return utils.new_document(source_path, settings=settings)        


def merge(d, **kwds):

    """
    Recursive dictionary merge, ie. multi-level `dict.update`.

    Set D[k] = kwds[k1..n][k] where D is any dictionary nested within `d`.
    Works like dict.update but recurses and updates nested dictionaries
    first.

    Returns in-place updated dict `d` for convenience.
    """

    # merge sublevels before overwriting on update
    for k in kwds:
        if isinstance( kwds[k], dict ):
            if k in d:
                subl = kwds[k]
                kwds[k] = merge( d[k], **subl )
    d.update(kwds)
    return d

def merge_level(d, *args, **kwds):
    """
    Update and/or return dictionary found in `d` by keys provided in `args`.
    """
    while args:
        d = d[args.pop()]
    if kwds:
        merge(d, **kwds)
    return d


"""
Document tree parsing, used by some convertors.
"""

def parse_list(list, split, item):
    "Parse each item from list. "
    for i in split(list):
        try:
            yield item(i)
        except ValueError, e:
            raise ValueError, "for item in list: %s" % e
        #list item %s: %s" % (i, e)

def parse_nested_list(tree, split, branch, item):
    "Traverse tree, branching to each sublevel, parsing each leaf. "
    "Each item can only contain one value. See nested_list_with_headers for a "
    "variant. "
    """
    - item 1
    - - item 2.1
      - item 2.2
      - - - item 2.3.1.1.1
    - item 3  
    """
    for sub in split(tree):
        if branch(sub[0]):
            yield list(parse_nested_list(sub[0], split, branch, item))
        else:
            yield item(sub[0])

def parse_nested_list_with_headers(tree, split, branch, head, item):
    "Item is leaf or has two values, one header (paragraph) and a sub-list. "
    """
    - branch 1

      - branch 1.1

        - leaf 1.1.1

      - leaf 1.2  

    - branch 2

      - leaf 2.1
    """
    for sub in split(tree):
        if branch(sub):
            subhead, subtail = head(sub)
            yield list((
                item(subhead),
                list(parse_nested_list_with_headers(subtail, split, branch, head, item))
                ))
        else:
            yield item(sub[0])

def is_du_list(node):
    return isinstance(node, nodes.enumerated_list) or\
            isinstance(node, nodes.bullet_list)

def is_du_headed_list(itemnode):
    return len(itemnode)==2 and isinstance(itemnode[0], nodes.paragraph) and\
            is_du_list(itemnode[1]) 

def du_nested_list_header(itemnode):
    return itemnode[0], itemnode[1]

def find_first_element(node, node_class):    
    while node:
        if isinstance(node, nodes.Element) and len(node) \
                and not isinstance(node, node_class):
            node = node[0]
        else:
            break
    if isinstance(node, node_class):
        return node


"""
Parsing/validating of data from document nodes.

Generic convertors for simple types from document nodes.

XXX: there are that accept document nodes, understand paragraphs or list.
XXX: how about flattening these, ie. blocks, references and other inline..
"""

def du_astext(node):
    "Flattens node. "
    if isinstance(node, nodes.Node):
        return node.astext()
    return node

def du_str(node):
    "Return unicode string, collapsed whitespace. "
    return re.sub('\s+', ' ', du_astext(node)).strip()  

def null_conv(datatype=str, conv=du_str):
    def du_null(node):
        arg = du_astext(node)
        if not arg:
            if datatype == str:
                return ''
            elif datatype == unicode:
                return u''
            elif datatype == float:
                return 0.0
            elif datatype == int:
                return 0
            return conv(arg)
        else:
            return conv(node)
    return du_null

def du_word(node):
    w = du_astext(node).strip()
    if ' ' in w:
        raise ValueError("Need a single word value without whitespace. ")
    return w

def du_int(node):
    return int(du_word(node))

def du_float(node):
    return float(du_word(node))

def du_text(node):
    "Multiline text. "
    return du_astext(node)

def du_uri_reference(node):
    rnode = find_first_element(node, nodes.reference)
    if not rnode:
        href = du_astext(node).strip()
    elif 'refuri' in rnode.attributes:
        href = rnode['refuri']
    if href:
        # XXX: relative or absolute
        m = uriref.match(href)
        if not m:
            raise ValueError, "Not a valid URI reference: %s" % href
        return href

def du_reference(node):
    rnode = find_first_element(node, nodes.reference)
    if not rnode:
        return None
    elif not isinstance(rnode, nodes.reference):        
        raise ValueError, "expected reference, not %r. " % rnode
    span = du_str(rnode)
    href = du_uri_reference(rnode['refuri'])
    return span, href

def du_flag(node):
    " No argument allowed.  "
    return directives.flag(du_astext(node))


"""
docutils.parser.rst.directives has some more argument validators which could
easy be added here by generating a wrapper for this series.

- flag
- path
- uri
- nonnegative_int
- percentage
- length_or_unitless
- length_or_percentage_or_unitless
- class_option
- unicode_code
- single_char_or_unicode
- single_char_or_whitespace_or_unicode
- positive_int
- positive_int_list
- encoding
- choice

Custom validators below.
"""

def choice(argument, values):
    """ Like docutils.parsers.rst.directives.choice but adjusted error
    reporting. """
    try:
        value = argument.lower().strip()
    except AttributeError:
        raise ValueError('must supply an argument; choose from %s'
                         % directives.format_values(values))
    if value in values:
        return value
    elif value:
        raise ValueError('"%s" unknown; choose from %s'
                         % (argument, directives.format_values(values)))
    else:
        raise ValueError('choose from %s'
                         % (directives.format_values(values)))

def du_bool(node):
    """
    Parse yes/no, on/off, true/false and 1/0. Return bool or null.
    """
    arg = du_astext(node).strip()
    if arg:
        opt = choice(du_astext(arg), ('yes', 'no', 'on', 'off', 'true',
            'false', '1', '0'))

        return opt in ('yes', 'on', 'true', '1')

def du_yesno(arg):
    """
    Parse yes/no, return bool or null.
    """
    arg = du_astext(arg).strip()
    if arg:
        opt = choice(arg, ('yes', 'no'))
        return opt == 'yes'

def cs_list(node):
    """
    Argument validator, parses comma-separated list.
    May contain empty values.
    """
    arg = du_astext(node).strip()
    if arg:
        return [a.strip() for a in arg.split(',')]
    else:
        return []#XXX:u'']

def ws_list(node):
    """
    Argument validator, parses white-space separated nodes.
    Cannot contain empty values.
    """
    items = re.sub('[\s ]+', ' ', du_astext(node).strip())
    if items:
        return items.split(' ')

def du_list(node):
    """
    Split a docutils list (bullet or enumerated) into its items.
    """
    return [item for item in node]


def conv_timestamp(data):
    pass # TODO

def conv_iso8801date(data):
    pass

def conv_rfc822date(data):
    pass


def null_validator(arg, datatype=str):
    "Return None equivalent for certain primitive types. " 
    if not arg:
        if datatype == str:
            return ''
        elif datatype == unicode:
            return u''
        elif datatype == float:
            return 0.0
        elif datatype == int:
            return 0
        return datatype(arg)

def nonzero_validator(vdscr):
    def validate_nonzero(arg, proc=None):
        if not arg:
            raise ValueError, "you must enter %s." % vdscr
        return True        
    return validate_nonzero        

def regex_validator(pattern, failmsg="invalid value: %(value)s", force=False):
    P = re.compile(pattern)
    def validate_regex(data, proc=None):
        if force or data:
            m = P.match(data)
            if not m:
                raise ValueError, failmsg % {'value': data}
        return True
    return validate_regex

def validate_email(data, proc=None):
    if not data:
        raise ValueError, "expected mailto reference"
    href = data
    if isinstance(data, tuple):
        span, href = data
    if not href.startswith('mailto:'):
        raise ValueError, "expected mailto reference, not %r" % href
    return True

def validate_absolute_uriref(data, proc=None):
    if not data:
        raise ValueError, "expected Absolute URI"
    href = data
    if isinstance(data, tuple):
        span, href = data
    m = uriref.match(href)
    if not m:
        raise ValueError, "does not match Absolute URI: %s" % href
    return True

"""
Corresponding Option parser validators.

Raise any exception or optparse.OptionValueError if needed.
"""

def validate_cs_list(setting, value, option_parser):
    ls = []
    for i in range(0,len(value)):
        v = value[i]
        if ',' in v:
            ls.extend( cs_list(v) )
        else:
            ls.append(v)
    return ls


def form_field_spec(value): 
    " Parse option value to spec for FormField construct.  "
    'id[,descr];type[;require[,append[,editable[,disabled]]]][;vldtors,]'
    partcnt = value.count(':')
    if partcnt < 1:
        raise "At least a field-id and datatype name is required. "
    elif partcnt > 3:
        raise "Too many fields in fieldspec. " # TODO: option spec parsing error
    parts = value.split(':')
    id_part = parts.pop(0)
    field_id, descr = id_part, ''
    if ',' in id_part:
        field_id, descr = id_part.split(',')
        descr = descr.strip('\'"')
    convertorname = parts.pop(0)
    kwds = {}
    kwds['help'] = descr
    if parts:
        attrs = parts.pop(0).split(',')
        keys = ['required','append','editable','disabled']
        while attrs:
            key = keys.pop(0)
            kwds[key] = du_bool(attrs.pop(0))
        if attrs:
            raise "Spec attributes out of bound. " # parsing error
    if parts:
        vldtor_part = parts.pop(0)
        kwds['validators'] = vldtor_part.split(',')        
    return (field_id, convertorname), kwds

def opt_form_field_spec(setting, value, option_parser):
    " Add or update form field specification.  "
    (nfid, nconv), nattr = form_field_spec(value.pop())
    for idx, ((fid, conv), attr) in enumerate(value):
        if fid == nfid:
            attr.update(nattr)
            value[idx] = fid, nconv, attr
            return value
    value.append((nfid, nconv, nattr))
    return value


# docutils component name
def component_name(obj, strip_module=True):
    clssobj = obj
    if isinstance(obj, type(obj)): # FIXME
        clssobj = obj.__class__
    cname = clssobj.__module__ +'.'+ clssobj.__name__
    # XXX: less confusing when uses (canonical) alias?
    # XXX: Builder class scope is always lost. 
    if strip_module:
        p = clssobj.__module__.rfind('.')
        #p = clssobj.__module__[p+1].rfind('.')
        return cname[p+1:]
    return cname


"""
Registry of convertors(/validators?) for form-framework and other user entry
parsers.

Note: list and tree convertors need to be used together with primitive type
convertors.

Any check that does not transform the data(-instance) can be put into a
validator instead.
"""

data_convertor = {
    'flag': du_flag,
    'bool': du_bool,
    'int': du_int,
    'float': du_float,
    'str': du_str,
    #'null': du_null,
    # XXX: 'null,str'?
    'null-str': null_conv(str, du_str),
    'text': du_text,
    'href': du_uri_reference,
    'ref': du_reference,
    'yesno': du_yesno,
    #'timestamp': conv_timestamp, 
    #'isodate': conv_iso8801date,
    #'rfc822date': conv_rfc822date,
    # list types
    'cs-list': (cs_list,),
    'ws-list': (ws_list,),
    'list': (du_list,),
    # misc. complex types
    'tree1': (du_list, is_du_list),
    'tree2': (du_list, is_du_headed_list, du_nested_list_header),
    #'du-deflist': du_definition_list, # nested dicts in form?
    #'du-enumlist': du_enumerated_list,
}

def get_convertor(type_name):
    if ',' in type_name:
        complextype_names = type_name.split(',')
        basetype = data_convertor[complextype_names.pop(0)]
        return basetype + tuple([ data_convertor[n] 
                for n in complextype_names ])
    else:
        return data_convertor[type_name]

validators = {
    'absolute-uri': validate_absolute_uriref,
    #'href': du_reference,
    'email': validate_email,
    #'timestamp': conv_timestamp, 
    #'isodate': conv_iso8801date,
    #'rfc822date': conv_rfc822date,
}
"Form validators.. "
#XXX: or split into form and option validators.. each has own call-spec.

"""
Parse settings from field-lists.
"""

# this is called option for now, but rewrite to form-framework...?

def extract_extension_options(fields, options_spec, raise_fail=True, errors=[]):
    """
    Inspired by ``docutils.utils.extract_extension_options``, this processes a
    field list or list of field nodes and parses the field values according
    to options_spec. In contrast with the DU utility, it allows more complex
    field names and bodies as is the case in e.g. processed references or lists?
    """
    """
    :Parameters:
        - `fields`: A list or field_list of fields with field_name, field_body pairs.
        - `options_spec`: Dictionary mapping known option names to a
          conversion function such as `int` or `float`.

    :Exceptions:
        - `UnknownOptionError` for unknown option names.
        - `DuplicateOptionError` for duplicate options.
        - `OptionValueError` for invalid option values (raised by conversion
           function).
        - `OptionTypeError` for invalid option value types (raised by conversion
           function).
    """
    options = {}
    seen = [] # track seen names, raise on missing required fields
    for field in fields:

        field_name, field_body = field[0:2]
        name = extract_field_name(field_name)

        if not name in options_spec or not options_spec[name][0]:
            error = UnknownOptionError( name, )        # if explicitly disabled
            if raise_fail:
                raise error
            errors.append((field, error))
            continue

        spec = options_spec[name]

        # XXX:BVB: dont like this
        convertor = spec[0]
        required = not (len(spec)>1 and spec[1])
        append = len(spec)>2 and spec[2]

        if name in options and not append:
            error = DuplicateOptionError( name, )
            if raise_fail:
                raise error
            errors.append((field, error))
            continue

        if name not in seen:
            seen.append(name)

        if len(field_body):
            pass

        error = None
        try:
            if not callable(convertor):
                body = field_body[0]
                if len(convertor)==2:
                    converted = list(parse_list(body, *convertor))
                elif len(convertor)==3:
                    converted = list(parse_nested_list(body, *convertor))
                elif len(convertor)==4:
                    converted = list(parse_nested_list_with_headers(body, *convertor))
            elif len(field_body):
                converted = convertor(field_body[0])
            else:
                converted = ''

        except ValueError, e:
            error = OptionValueError( name, field_body, e )
        except TypeError, e:
            error = OptionValueError( name, field_body, e )
        if error:
            if raise_fail:
                raise error
            errors.append((field, error))
            continue

        if append:
            if not name in options:
                options[name] = []
            if isinstance(converted, list):
                options[name].extend(converted)
            else:
                options[name].append(converted)
        else:
            options[name] = converted

    if len(options_spec) > len(seen):
        # Report missing fields
        names = options_spec.keys()
        [names.remove(name) for name in seen]
        for name in names:
            spec = options_spec[name]
            if len(spec)<2 or spec[1]:
                error = MissingOptionError(name,)
                if raise_fail:
                    raise error
                errors.append((None, error))

    return options

def extract_field_name(field_name):
    name = re.sub('[^\w]+', '-', field_name.astext())
    return name
# Du impl.
    if len(field[0].astext().split()) != 1:
        raise BadOptionError(
            'extension option field name may not contain multiple words')
    name = str(field[0].astext().lower())


# Du impl.
    body = field[1]
    if len(body) == 0:
        data = None
    elif len(body) > 1 or not isinstance(body[0], nodes.paragraph) \
          or len(body[0]) != 1 or not isinstance(body[0][0], nodes.Text):
        raise BadOptionDataError(
              'extension option field body may contain\n'
              'a single paragraph only (option "%s")' % name)
    else:
        data = body[0][0].astext()

"""
Errors from parsing field-lists as options.
"""

class UnknownOptionError(utils.ExtensionOptionError):
    def __str__(self):
        return "unknown option `%s`. " % self.args

class DuplicateOptionError(utils.DuplicateOptionError):
    def __str__(self):
        return "duplicate option `%s`. " % self.args

class OptionTypeError(utils.BadOptionDataError):
    def __str__(self):
        name, data, e = self.args
        return "invalid value type '%s' for option `%s`:\n\n\t%s " % (
                data, name, e)

class OptionValueError(utils.BadOptionDataError):
    def __str__(self):
        name, data, e = self.args
        return "invalid value '%s' for option `%s`:\n\n\t%s " % (
                data, name, e)

class MissingOptionError(utils.ExtensionOptionError):
    def __str__(self):
        return "missing option `%s`. " % self.args


# Utility add-class transform

def addClass(classnames):
    "Create a new transform to set one or more classnames."

    class AddClass(include.Include):
        default_priority = 500

        add_class = []

        def apply(self):
            for add_class in self.add_class:
                xpath, klass = add_class.split(',')
                loc = self.find_location(xpath)
                loc['classes'].append(klass)
    AddClass.add_class = classnames
    return AddClass


"""
Regex field-list parsing.
"""

field_re = '^\s*:%s:\s*([a-zA-Z0-9\.,\ _-]+)\s*$'

def extract_field(source, field, default=None, strip=False):
    # TODO: configurable body regex
    # TODO: case insensitive option
    m = re.compile(field_re % field, re.M).search(source)
    if m:
        return m.groups()[0].strip()
    else:
        return default
    assert not strip, "TODO, remove field lines from source. "

def extract_modeline(source, strip=False):
    pass # TODO: extract_modeline

def read_buildline(source, strip=False,
        default_package='standalone',
        default_class='Document',
        field_name='build'):
    "Read builder package and class-name from sentinel line formatted as rSt field.  "

    builder_name = extract_field(source, field_name, strip=strip)
    if not builder_name:
        return default_package, default_class

    for c in ('.', ' '):
        p = builder_name.rfind(c)
        if p == -1:
            continue
        package = builder_name[:p].replace('-', '_')
        return package, builder_name[p+1:]

    return builder_name, default_class


"""
Document visitors.
"""

class FieldListVisitor(nodes.SparseNodeVisitor):

    """
    Nabu has a FieldListVisitor but that returns dictionaries.

    This simply gathers all fields into a list, which should be fine as its
    treated as iterable.
    """

    def __init__(self, *args, **kwds):
        nodes.SparseNodeVisitor.__init__(self, *args, **kwds)

    def apply(self):
        self.initialize()
        self.document.walkabout(self)

    def initialize(self):
        self.field_list = []

    def visit_field(self, node):
        assert len(node.children) == 2
        self.field_list.append(node)


def first_and_last_field_list(document):
    """
    """
    field_lists = document.traverse(nodes.field_list)

    if len(field_lists) == 1:
        return (field_lists[0],)

    elif len(field_lists):
        return (field_lists[0], field_lists[-1])

    else:
        return ()
        

