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
from itertools import chain

from dotmpe.du import util
from nabu import extract
from nabu.extract import \
        Extractor, \
        ExtractorStorage, \
        SQLExtractorStorage as PgSQLExtractorStorage


logger = util.get_log(__name__)

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


class SQLiteExtractorStorage(extract.ExtractorStorage):

    """
    Extractor storage base class for storage that uses a DBAPI-2.0 connection.

    Note: all of the declared tables should have a non-null unid column, to
    enable clearing obsolete data when reloading a source document.
    """

    # Override this in the derived class.
    # This should be a map from the table name to the table schema.

    # Tables that have a unid mapping.  The data associated with the document's
    # unid are cleared automatically.
    sql_relations_unid = []

    # Accessory tables that do not have a unid mapping.
    sql_relations = []

    def __init__(self, module, connection):
        self.module, self.connection = module, connection

        logger.debug("New SQLiteExtractorStorage for %s, with %s", module,
                connection)

        cursor = self.connection.cursor()

        # Check that the database tables exist and if they don't, create them.
        for tname, rtype, schema in chain(self.sql_relations_unid,
                                          self.sql_relations):
            cursor.execute("SELECT * FROM main.sqlite_master "
                "WHERE type='table' "
                "AND name = ? ", (tname,))
            if cursor.rowcount <= 0:
                logger.info("Creating DB schema %s (%s)", tname, rtype)
                cursor.execute(schema)

        self.connection.commit()

    def clear(self, unid=None):
        """
        Default implementation that clears the entries/tables.
        """
        cursor = self.connection.cursor()

        for tname, rtype, schema in self.sql_relations_unid:
            query = "DELETE FROM %s" % tname
            if unid is not None:
                query += " WHERE unid = '%s'" % unid
            cursor.execute(query)

        self.connection.commit()

    def reset_schema(self):
        """
        Default implementation that drops the tables.
        """
        cursor = self.connection.cursor()

        for tname, rtype, schema in chain(self.sql_relations_unid,
                                          self.sql_relations):

            # Indexes are automatically destroyed with their attached tables,
            # don't do it explicitly.
            if rtype.upper() == 'INDEX':
                continue

            x = cursor.execute("""
                SELECT * FROM main.sqlite_master WHERE type='table'
                AND name = ?
               """, (tname,))

            try:
                cursor.fetchone()
                cursor.execute("DROP %s %s" % (rtype, tname))
                logger.info("Destroyed table %s", tname)
            except Exception, e:
                print e

            cursor.execute(schema)

        self.connection.commit()



