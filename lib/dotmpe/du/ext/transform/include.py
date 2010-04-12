"""
Include chunks of data to the document.

May be used to include external raw xml, latex or html data in the document
at publication time. 
"""
from docutils.transforms import Transform


class Include(Transform):

    """
    This is a helper class for transforms that need to insert at certain
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
                {'action':'append', 'default':[], 'metavar':'PATH[IDX],DATA'}
            ),
            )

    default_priority = 50
    "Way in front of any other transform on the tree. "

    def apply(self):
        inserts = [i.split(',') for i in self.document.settings.include]

        decoration = self.document.get_decoration()
        for p, data in inserts:
            # parse path
            path, index = self.parse_xpath(p)
            if hasattr(decoration, 'get_'+path):
                loc = getattr(decoration, 'get_'+path)()
            else:
                loc = self.find_location(path)
            # process data
            # insert
            loc.insert(index, data)

    xpath_re = r'([a-z][a-z0-9_])([([0-9]+)])?'

    def parse_xpath(self, path):
        match = re.compile(xpath_re).match
        parts = path.split('/')
        for p in parts:
            print match(p)
        return 'header', 0            

    def find_location(self, path):
        pass

    def parse_xml(self, xml):
        pass

