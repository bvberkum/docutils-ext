from dotmpe.du.ext import extractor
from nabu.extractors.document import Storage as PgSQLExtractorStorage


class Storage(extractor.SQLiteExtractorStorage, PgSQLExtractorStorage):

    def __init__(self, *args, **kwds):
        extractor.SQLiteExtractorStorage.__init__(self, *args, **kwds)

