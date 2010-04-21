import re
from docutils import utils, nodes
#from docutils.nodes import fully_normalize_name, make_id
from dotmpe.du.ext.transform import include
# this has some handy argument handlers
from docutils.parsers.rst import directives


# Helper function

def parse_list(list, split, item):
    "Parse each item from list. "
    for i in split(list):
        yield item(i)

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

# Validators, used on field body

def du_str(node):
    return __astext(node)

def du_int(node):
    return int(__astext(node))

def du_float(node):
    return float(__astext(node))

#def du_uri(node):
#    arg = __astext(node)
#    return directives.uri(node.astext())

def du_flag(node):
    return directives.flag(__astext(node))

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

# XXX: what about flattening references and other inline..
def yesno(node):
    """
    Argument parser/validator.
    """
    return directives.choice(__astext(node), ('yes', 'no'))

def cs_list(node):
    """
    Argument validator, parses comma-separated list.
    May contain empty values.
    """
    arg = __astext(node).strip()
    if arg:
        return [a.strip() for a in arg.split(',')]
    else:
        return [u'']

def ws_list(node):
    """
    Argument validator, parses white-space separated nodes.
    Cannot contain empty values.
    """
    items = re.sub('[\s ]+', ' ', __astext(node).strip())
    if items:
        return items.split(' ')

def du_list(node):
    """
    Split a docutils list (bullet or enumerated) into its items.
    """
    return [item for item in node]


# this is called option for now, but rewrite to form-framework...?
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

def extract_extension_options(fields, options_spec, raise_fail=True, errors=[]):
    """
    Inspired by ``docutils.utils.extract_extension_options``, this processes a
    field list or list of field nodes and parses the field values according
    to options_spec. In contrast with the DU utility, it allows more complex
    field names and bodies as is the case in e.g. processed references or lists.
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

def __astext(node):
    if isinstance(node, nodes.Node):
        return node.astext()
    return node


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


field_re = '^\s*:%s:\s*([a-zA-Z0-9\.,\ _-]+)\s*$'

def extract_field(source, field, strip=False):
    m = re.compile(field_re % field, re.M).search(source)
    if m:
        return m.groups()[0].strip()
    assert not strip, "TODO"

def extract_modeline(source, strip=False):
    pass # TODO: extract_modeline

def read_buildline(source, strip=False,
        default_module='standalone',
        default_class='Document',
        field_name='build'):
    "Return the appropiate builder module and class-name for the given source. "
    # FIXME: field_name should be coordinated by specreader?
    # XXX: what about other line-forms like mode line?

    field = extract_field(source, field_name, strip=strip)
    if not field:
        return default_module, default_class

    for c in ('.', ' '):
        p = field.rfind(c)
        if p == -1:
            continue
        module = field[:p].replace('-', '_')
        return module, field[p+1:]

    return field, default_class

