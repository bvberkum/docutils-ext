from docutils import nodes
from nabu import extract
from docutils.utils import extract_extension_options


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


class FormExtractor(extract.Extractor):

    """
    Treat certain or all field lists from document as form-fields.
    Use the option_spec to specify which fields to extract and with what
    validator.

    Does not alter the tree.

    This is like the UserSpec transform's, except that it is designed to operate
    as Extractor?
    """

    default_priority = 500

    option_spec = {}

    def apply(self, unid=None, storage=None, **kwds):
        v = FieldListVisitor(self.document)
        v.apply()
        try:
            settings = extract_extension_options(v.field_list, self.option_spec)
            #self.validate(settings)
        except Exception, e:
            self.document.reporter.error("Error processing form: %s" % e)

    def validate(self, settings):
        # no-op, override for further sanity checks
        return settings


class FormStorage(extract.Storage):
    def store(self, unid, settings):
        pass

