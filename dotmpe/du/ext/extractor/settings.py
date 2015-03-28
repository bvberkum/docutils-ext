from nabu import extract

from dotmpe.du.ext import extractor




class Extractor(extract.Extractor):

    default_priority = 0

    settings_spec = ()

    def apply(self, unid=None, storage=None, **kwargs):
        settings = self.document.settings
        from pprint import pformat
        self.document.reporter.info("Running document settings extractor for %s" % unid)
        #self.document.reporter.info('Document settings extractor: %s' % settings)
        storage.store(unid, settings)


class SettingsStorage(extractor.TransientStorage):

# TODO settings storage
    pass


