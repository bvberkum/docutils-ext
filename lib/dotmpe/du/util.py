import re
from docutils import utils
#from docutils.nodes import fully_normalize_name, make_id
from dotmpe.du.ext.transform import include
from docutils.parsers.rst import directives


def yesno(argument):
    """
    Argument parser/validator.
    """
    return directives.choice(argument, ('yes', 'no'))

def cs_list(argument):
    """
    Argument validator, parses comma-separated list.
    May contain empty values.
    """
    return [a.strip() for a in argument.split(',')]

def ss_list(argument):
    """
    Argument validator, parses white-space separated arguments.
    Cannot contain empty values.
    """
    argument = re.sub('\s ]+', ' ', argument.strip())
    return argument.split(' ')


def extract_extension_options(fields, option_spec):
    """
    Inspired by ``docutils.utils.extract_extension_options``, this processes a
    field list or list of field nodes and parses the field values according
    to option_spec. In contrast with the DU utility, it allows more complex
    field names and bodies as is the case in e.g. processed references or lists.
    """
    option_list = extract_options(fields)
    option_dict = utils.assemble_option_dict(option_list, option_spec)
    return option_dict

def extract_options(field_list):
    """
    Return a list of option (name, value) pairs from field names & bodies.
    This is a more lenient version of ``docutils.utils.extract_options``.
    """
    option_list = []
    for field in field_list:
        name = re.sub('[^\w]+', '-', field[0].astext())
        body = field[1]
        if len(body) == 0:
            data = None
        else:
            data = body[0][0].astext()
        option_list.append((name, data))
    return option_list


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

