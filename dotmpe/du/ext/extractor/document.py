from dotmpe.du.ext import extractor
from nabu.extractors.document import Storage as PgSQLExtractorStorage


class Storage(extractor.SQLiteExtractorStorage, PgSQLExtractorStorage):

    def __init__(self, *args, **kwds):
        print self.__class__.__name__, kwds['connection']
        extractor.SQLiteExtractorStorage.__init__(self, *args, **kwds)

