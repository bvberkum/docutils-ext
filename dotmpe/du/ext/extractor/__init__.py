"""
Extractor modules and misc.

Interface::

    class Extractor(docutils.transforms.Transform):
        @classmethod
        def init_parser(cls): 
            pass
        def apply(self, **kwargs):
            pass

    class ExtractorStorage:
        def store(self, unid, *args):
            pass
        def clear(self, unid=None):
            pass
        def reset_schema(self):
            pass

One default storage implementation does not make much sense.
Storage types depend on host system.

Types come from:

- Relational Databases, presumably MSSQL, PGSQL, MySQL.
- Django and its db model.
- GAE or Google app-engine big table datastore models.

A transient storage type is defined here, as superclass for     
for extractor modules, such as the ``form`` extractor?
"""
from nabu import extract


class TransientStorage(extract.ExtractorStorage):
    "This keeps all extracted data on the instance. "

    def __init__(self, init={}, datakey='_storage', specs=None):
        assert datakey not in self.__dict__
        setattr(self, datakey, init)
        self.datakey = datakey
        self.defaults = init
        self.specs = None

    def __getdata__(self):
        return getattr(self, self.datakey)
    def __setdata__(self, newvalue):
        return setattr(self, self.datakey, newvalue)
    data = property(__getdata__, __setdata__)

    def store(self, source_id, *args, **kwds):
        self.data[source_id] = args, kwds

    def clear(self, source_id):
        self.data[source_id] = self.defaults

    def reset_schema(self, source_id=None):
        "???"
        raise NotImplemented


class SimpleSourceMap(extract.ExtractorStorage): pass # TODO
    # define source_id -> value_blob storages

class ComplexDictSourceMap(extract.ExtractorStorage): pass
    # define source_id -> key, value mapping storages

