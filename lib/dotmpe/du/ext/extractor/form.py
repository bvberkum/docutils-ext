"""
Extractors and util to retrieve and validate user-data from a document.

TODO: this does not validate against documents original settings_spec yet.
"""
from docutils import nodes, DataError
from nabu import extract
from dotmpe.du import extractor
from dotmpe.du import util
#from dotmpe.du.ext.transform import user



class FormExtractor(extract.Extractor):#, user.UserSettings):

    """
    Treat certain or all field lists from document as form-fields.
    Use the option_spec to specify which fields to extract and with what
    validator.

    Does not alter the tree.

    This is like the UserSettings transform's, with a wrapper to operate
    as Extractor.
    """

    default_priority = 500

    settings_spec = (
        )
    "TODO: settings for extractors. "

    options_spec = {}
    # XXX: see comments elsewhere, this will/should change..

    validate = None
    "Hook for additional sanity check. "

    def apply(self, unid=None, storage=None, **kwds):
        v = util.FieldListVisitor(self.document)
        v.apply()
        settings = self.extract_fields(v.field_list)
        storage.clear(unid)
        storage.store(unid, settings)
       
    # TODO: merge FormExtractor.extract_fields with UserSettings..       
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
        # instance variables..
        if self.validate:
            try:
                return self.validate(settings)
            except (AssertionError, DataError), e:
                sysmsg = self.document.reporter.error(
                        str(e))
                self.document.append(sysmsg)

        return settings


class FormStorage(extractor.TransientStorage):
    "Special storage for form values. "
    "This keeps the form dict for each document. "

    def __init__(self):
        self.form_settings = {}

    def store(self, source_id, settings):
        self.form_settings[source_id] = settings

    def clear(self, source_id):
        self.form_settings[source_id] = {}

    def reset_schema(self, source_id):
        raise NotImplemented


