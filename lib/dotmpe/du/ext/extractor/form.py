"""
Extractors and utilities to retrieve and validate user-data from a document.
"""
from docutils import nodes
from nabu import extract
from dotmpe.du import util


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

    def validate(frmextr, settings):
        "Hook for additional sanity check. "
        return settings

    def apply(self, unid=None, storage=None, **kwds):
        v = FieldListVisitor(self.document)
        v.apply()
        settings = {}
        try:
            settings = util.extract_extension_options(v.field_list, self.option_spec)
            if not settings:
                return
            if self.validate:
                settings = self.validate(settings)
        except Exception, e:
            self.document.reporter.error("Error processing form: %s" % e)
        #storage.clear(unid)
        storage.store(unid, settings)
        

# Storage API and simple implementation

class FormStorage(extract.ExtractorStorage):
    def store(self, source_id, settings):
        raise NotImplemented

    def clear(self, source_id):
        raise NotImplemented

    def reset_schema(self, source_id):
        raise NotImplemented


class SimpleFormStorage(FormStorage):
    "This only keeps the settings on the instance. "

    def __init__(self):
        self.document_settings = {}

    def store(self, source_id, settings):
        self.document_settings[source_id] = settings

