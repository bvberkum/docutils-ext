from nabu import extract

from dotmpe.du import util
from script_mpe.taxus.util import get_session



class InventoryExtractor(extract.Extractor):

    """
    TODO: store names with types in common name table
    TODO: scan inventory definition blocks for stock lines
    """

    settings_spec = (
        'Inventory Extractor Options',
        "Depends on the Title extractor's storage. ",
        ((
        ),(
             'Database to store stock count. ',
             ['--inventory-database'],
             {
                 'metavar':'PATH', 
                 'validator': util.optparse_init_anydbm,
             }
        ),)
    )

    default_priority = 500

    # See dotmpe.du.form for settings_spec

    def init_parser(cls):
        " do some env. massaging if needed. "

    fields_spec = []

    def apply(self, unid=None, storage=None, **kwds):
        pass


class InventoryStorage(extract.ExtractorStorage):

    def __init__(self, dbref=None, initdb=False):
        assert dbref, self
        #print 'InventoryStorage', 'init', dbref, initdb
        self.sa = get_session(dbref, initdb)

    def store(self, source_id, *args):
        print 'store', source_id, args

    def clear(self, source_id):
        pass

    def reset_schema(self, source_id):
        raise NotImplemented

