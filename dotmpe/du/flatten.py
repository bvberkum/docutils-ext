"""
TODO: just an idea for another (X)HTML writer, not based on visitor pattern?

Translating registry of flatteners.

Ie. xhtml.document flattens a document to valid XHTML frame?
"""
from docutils import nodes


#
# registry of flatteners 
#   
__registry = { }

def register_flattener ( o, f ):
    __registry [ o ] = f
    
def unregister_flattener ( o ):
    try:
        del __registry [ o ]
    except KeyError: 
        pass

def registry ( ):
    '''mostly for debugging'''
    return __registry 

def get_registered_flattener ( o ):
    return __registry [ o ]

def flatten ( o ): 
    try:
        return __registry [ type ( o ) ] ( o )
    except KeyError:
        return unicode ( o )


# Based on Breve's tags and flatten which in turn borrowed from Nevow's tags.

class Proto ( unicode ):
    __slots__ = [ 'Class' ]
    Class = Tag
    def __call__ ( self, **kw ):
        return self.Class ( self )( **kw )

    def __getitem__ ( self, children ):
        return self.Class ( self )[ children ]

    def __str__ ( self ):
        return unicode ( self.Class ( self ) )

class cdata ( unicode ):
    def __init__ ( self, children ):
        self.children = children

    def __str__ ( self ):
        return u'<![CDATA[%s]]>' % self.childre

class xml ( unicode ): pass
def flatten_xml ( o ):
    return o

class comment ( unicode ): pass
def flatten_comment ( o ):
    return u"\n<!--\n%s\n-->\n" % o

# Standard flatteners.
def flattened_tags ( o ):
    '''generator that yields flattened tags'''
    def flattened ( o ):
        if o.render:
            o = o.render ( o, o.data )
            if not isinstance ( o, nodes.Node ):
                yield flatten ( o )
                raise StopIteration

        yield u'<%s%s>' % ( o.name, u''.join ( quoteattrs ( o.attrs ) ) )
        for c in o.children:
            yield flatten ( c )
        yield u'</%s>' % o.name
        raise StopIteration
    return flattened ( o )

def flatten_tag ( o ):
    return  ''.join ( flattened_tags ( o ) )

def flatten_proto ( p ):
    return u'<%s />' % p

def flatten_sequence ( o ):
    return u''.join ( [ flatten ( i ) for i in o ] )

def flatten_callable ( o ):
    return flatten ( o ( ) )

register_flattener ( list, flatten_sequence )
register_flattener ( tuple, flatten_sequence )
register_flattener ( Proto, flatten_proto )
register_flattener ( Tag, flatten_tag )
register_flattener ( str, lambda s: escape ( unicode ( s, 'utf-8' ) ) )
register_flattener ( unicode, escape )
register_flattener ( cdata, unicode )
register_flattener ( comment, flatten_comment )
register_flattener ( xml, flatten_xml )
register_flattener ( type ( lambda: None ), flatten_callable )



