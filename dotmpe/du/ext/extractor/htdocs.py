"""
.mpe htdocs extractor
"""
from nabu import extract
#from dotmpe.du.ext import extractor


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
        # - get (new) ref for each definition term
        # - accumulated definition descriptions:
        #   append lists to some log,
        #   
        print unid, storage, kwds


class HtdocsStorage(extract.ExtractorStorage):

    def __init__(self, *args, **kwds):
        print 'HtdocsStorage', 'init', args, kwds

    def store(self, source_id, *args):
        pass

    def clear(self, source_id):
        pass

    def reset_schema(self, source_id):
        raise NotImplemented


Extractor = HtdocsExtractor
Storage = HtdocsStorage

