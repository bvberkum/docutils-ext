"""
.mpe htdocs extractor
"""
from nabu import extract
#from dotmpe.du.ext import extractor
from script_mpe import htdocs, taxus



class HtdocsExtractor(extract.Extractor):

    """
    See dotmpe.du.form for documentation.
    """

    default_priority = 500

    # See dotmpe.du.form for settings_spec

    def init_parser(cls):
        " do some env. massaging if needed. "

    fields_spec = []

    def apply(self, unid=None, storage=None, **kwds):
        print 'apply', unid, storage, kwds
        storage.store(unid)


class HtdocsStorage(extract.ExtractorStorage):

    def __init__(self, *args, **kwds):
        print 'HtdocsStorage', 'init', args, kwds
        #self.sa = taxus.get_session()

    def store(self, source_id, *args):
        print 'store', source_id, args

    def clear(self, source_id):
        pass

    def reset_schema(self, source_id):
        raise NotImplemented


Extractor = HtdocsExtractor
Storage = HtdocsStorage

