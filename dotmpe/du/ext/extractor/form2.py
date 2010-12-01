"""
Extractors and util to retrieve and validate user-data from a document.
"""
import logging
from nabu import extract
from dotmpe.du import form
from dotmpe.du.ext import extractor


logger = logging.getLogger('dotmpe.du.ext.extractor.form2')

class FormExtractor(extract.Extractor):

    """
    See dotmpe.du.form for documentation.
    """

    default_priority = 500

    # See dotmpe.du.form for settings_spec

    def init_parser(cls):
        " do some env. massage if needed. "

    fields_spec = []

    def apply(self, unid=None, storage=None, **kwds):
        " process and validate found entries. "
        if not unid or not storage: return
        pfrm = form.FormProcessor.get_instance(self.document, self.fields_spec)
        pfrm.process_fields()
        settings = self.document.settings
        form_process = getattr(settings, 'form_process', 'validate')
        if form_process == 'prepare':
            return # not an extract task
        if form_process == 'validate':
            return # validation should be done
        valid = getattr(settings, 'validated', False)
        if not valid:
            self.document.reporter.system_message(
                    3, 'Invalid form cannot be applied to storage. ',)
        elif form_process == 'submit':
            logging.info('Applying FormExtractor. ')
            storage.store(unid, pfrm.values)
            #for fid, value in pfrm.values.items():
            #    storage.store(unid, fid, value)
        else:
            raise KeyError, "Unknown action %r" % form_process

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


