import re


trailing_ws = re.compile('^.*(?<!\s)(\s+)$')

def get_trailing_ws(string):
    assert isinstance(string, str) or isinstance(string, unicode), string
    m = trailing_ws.match(string)
    if m:
        return m.group(1)
    return ''

is_all_ws = re.compile('^\s+$').match
    
def attr(node, name):
    """
    Helper function. Return attribute from dict if set.
    """
    if name in node and node[name]:
        return node[name]

class ContextStack(object):
    """A stack of states. Setting an attribute overwrites the last
    value, but deleting the value reactivates the old one.
    Default values can be set on construction.
    
    This is used for important states during output of rst,
    e.g. indent level, last bullet type.
    """
    
    def __init__(self, defaults=None):
        '''Initialise _defaults and _stack, but avoid calling __setattr__'''
        if defaults is None:
            object.__setattr__(self, '_defaults', {})
        else:
            object.__setattr__(self, '_defaults', dict(defaults))
        object.__setattr__(self, '_stack', {})

    def __getattr__(self, name):
        '''Return last value of name in stack, or default.'''
        if name in self._stack:
            return self._stack[name][-1]
        if name in self._defaults:
            return self._defaults[name]
        raise AttributeError

    def append(self, name, value):
        l = list(getattr(self, name))
        l.append(value)
        setattr(self, name, l)

    def __setattr__(self, name, value):
        '''Pushes a new value for name onto the stack.'''
        if name in self._stack:
            self._stack[name].append(value)
        else:
            self._stack[name] = [value]

    def __delattr__(self, name):
        '''Remove a value of name from the stack.'''
        if name not in self._stack:
            raise AttributeError
        del self._stack[name][-1]
        if not self._stack[name]:
            del self._stack[name]
   
    def depth(self, name):
        l = len(self._stack[name])
        if l:
            return l-1

    def __contains__(self, name):
        return name in self._stack

    def previous(self, name):
        if len(self._stack[name]) > 1:
            return self._stack[name][-2]

    def __repr__(self):
        return repr(self._stack)


def classname(obj):
    return obj.__class__.__name__



