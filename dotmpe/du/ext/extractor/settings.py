from nabu import extract


class Extractor(extract.Extractor):

    default_priority = 0

    settings_spec = ()

    def apply(self, unid=None, storage=None, **kwargs):
        settings = self.document.settings
        from pprint import pformat
        self.document.reporter.info(
            'Document settings extractor: %s' % pformat(settings))
        storage.store(unid, settings)


