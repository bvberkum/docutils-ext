"""
Extractors and utilities to retrieve and validate user-data from a document.
"""
from docutils import nodes, DataError
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

    options_spec = {}

    validate = None
#    def validate(frmextr, settings):
#        "Hook for additional sanity check. "
#        return settings

    def apply(self, unid=None, storage=None, **kwds):
        v = FieldListVisitor(self.document)
        v.apply()
        settings = self.extract_fields(v.field_list)
        #storage.clear(unid)
        storage.store(unid, settings)
        
    def extract_fields(self, fields):
        settings = {}
        errors = []

        settings = util.extract_extension_options(fields, self.options_spec,
                raise_fail=False, errors=errors)

        for field, error in errors:
            sysmsg = self.document.reporter.error(
                    #"Error processing value.\n"+
                    str(error))
            if field:
                if len(field[1]):
                    field[1].clear()
                field[1].append(sysmsg)
                    
            else:
                # XXX:BVB: gather later by universal.Messages
                self.document.append(sysmsg)

        if not settings:
            return

        # XXX: could rather defer sanity check to storage, which accepts
        # instance variables.
        if self.validate:
            try:
                return self.validate(settings)
            except (AssertionError, DataError), e:
                sysmsg = self.document.reporter.error(
                        str(e))
                self.document.append(sysmsg)

        return settings

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

