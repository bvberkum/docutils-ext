"""
Extractors and util to retrieve and validate user-data from a document.
"""
from nabu import extract
from dotmpe.du import form
from dotmpe.du.ext import extractor


class FormExtractor(extract.Extractor):

    """
    See dotmpe.du.form for documentation.
    """

    default_priority = 500

    # See dotmpe.du.form for settings_spec

    form_spec = {}

    def init_parser(cls):
        " do some env. massage if needed. "

    def apply(self, unid=None, storage=None, **kwds):
        " process and validate found entries. "
        specs = self.form_spec or settings.get('form_spec', {})
        pfrm = form.FormProcessor(self.document, specs)
        pfrm.process_fields()

        return
        #
        # Old
        #v = util.FieldListVisitor(self.document)
        #v.apply()
        #settings = self.extract_fields(v.field_list)
        #storage.clear(unid)
        #storage.store(unid, settings)
       
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
                # XXX:BVB: gathered later by universal.Messages
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
    """
    Special storage for form values.
    This keeps the form dict for each document. 
    """

    def __init__(self):
        self.form_settings = {}

    def store(self, source_id, settings):
        self.form_settings[source_id] = settings

    def clear(self, source_id):
        self.form_settings[source_id] = {}

    def reset_schema(self, source_id):
        raise NotImplemented


