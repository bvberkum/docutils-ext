""":created: 2010-04-11
:author: B. van Berkum

Include chunks of data into the document.

Use to include external raw xml, latex or html data in the document
at publication time. 
"""
import re
from docutils import nodes
from docutils.transforms import Transform


class Include(Transform):

    """
    This is a helper baseclass for transforms that need to insert at certain
    locations. It can be used on itself to insert raw nodes too.
    """

    settings_spec = (
            (
                'Provide unparsed, raw content to insert at location. '
                'Multiple values pairs are accepted. '
                'Paths may be decorator names, otherwise the path must exist '
                'in the document. Use index -1 for append and 0 for prepend. '
                'Data may be raw string prefixed by ``type:``. '
                'Use a second ``file:`` prefix to read raw data from filename. ',
                ['--include'], 
                {'action':'append', 'default':[], 'metavar':'XPATH,IDX,DATA', 
                    #TODO:'validate': util.xpath_insert
                }
            ),)

    default_priority = 180
    "Before actual substitution. "

    datav_re = r'^(latex|html|xml):(file:)?(.*)$'

    def apply(self):
        if not hasattr(self.document.settings, 'include'):
            return

        # validate options
        inserts = [i.split(',') for i in self.document.settings.include]
        for i in range(0, len(inserts)):
            if len(inserts[i]) != 3:
                raise ""
            else:
                inserts[i][1] = int( inserts[i][1] )

        # insert each value
        for xpath, index, data in inserts:

            loc = self.find_location(xpath)

            # process data
            m = re.compile(self.datav_re).match(data)
            if not m:
                raise "Unable to read: %s" % data

            datatype, isfile, data = m.groups()
            assert not isfile
#            if isfile:
#                assert document.settings.include
#                data = open(data).read()

            # insert
            if index < 0:
                index = len(loc)+index+1
            loc.insert(index, nodes.raw('', data, format=datatype))


    xpath_re = r'([a-z]?[a-z0-9_]+)(?:\[([0-9]+)\])'

    def parse_xpath(self, path):
        match = re.compile(self.xpath_re).match
        parts = path.split('/')
        path = []
        for p in parts:
            g = match(p).groups()
            path.append((g[0], int(g[1])))
        return path            

    def find_location(self, path):
        decoration = self.document.get_decoration()
        if hasattr(decoration, 'get_'+path):
            return getattr(decoration, 'get_'+path)()

        else:
            # use xpath to retrieve parent node
            parts = self.parse_xpath(path)

            doc = self.document
            if parts[0][0] == 'document':
                parts.pop(0)

            while parts:
                name, index = parts.pop(0)
                for e in doc:
                    if isinstance(e, getattr(nodes, name)):
                        if index == 0:
                            doc = e
                            break
                        index -= 1

            assert not parts, 'illegal path %s' % path                            
            return doc


