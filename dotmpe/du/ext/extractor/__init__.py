"""
Extractor modules and misc.

One default storage implementation does not make much sense.

Storage types depends on host system.

Types are:
    - SQL, but presumably also MSSQL, PGSQL, MySQL.
    - Django for its db model.
    - GAE for Google app-engine's datastore specific model.

A transient storage type is defined here, as superclass for     
for extractor modules, such as the ``form`` extractor?
"""
from nabu import extract


class TransientStorage(extract.ExtractorStorage):
    "This only keeps the settings on the instance. "

    def __init__(self):
        self.data = ()

    def store(self, source_id, *args, **kwds):
        self.data[source_id] = args, kwds

    def clear(self, source_id):
        self.data[source_id] = ()

    def reset_schema(self, source_id):
        raise NotImplemented


