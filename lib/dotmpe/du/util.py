import re
#from docutils.nodes import fully_normalize_name, make_id
from dotmpe.du.ext.transform import include


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
    pass


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

