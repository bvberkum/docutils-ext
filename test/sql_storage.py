"""
Test dotmpe.du.ext.extractor..

The DBAPI-2.0 connection Storage wrapper in nabu looks like a PostrgreSQL wrapper really.

TODO: just the beginning of extractor testing.

"""
import os

import unittest
import sqlite3

from dotmpe.du.ext.extractor import SQLiteExtractorStorage


class TestStorage( SQLiteExtractorStorage ):

    sql_relations_unid = [
        ('test_table', 'TABLE', '''
            CREATE TABLE test_table (
                unid VARCHAR PRIMARY KEY,
                label VARCHAR NOT NULL
            )
        '''), ]

    sql_relations = [
        ('var_idx', 'INDEX',
             """CREATE INDEX var_idx ON test_table (label)"""), ]


class StorageTest(unittest.TestCase):

    def test__storage(self):
        dbref = './test.db'
        connection = sqlite3.connect(dbref)
        c = connection.cursor()
        c.fetchone()

        store = TestStorage( None, connection )
        store.reset_schema()
        c.execute("""INSERT INTO test_table (unid, label) VALUES ('a', 'Foo') """)
        c.execute("""INSERT INTO test_table VALUES ('b', 'Bar') """)

        c.execute(""" SELECT * from test_table """)
        self.assertEquals( len( c.fetchall() ), 2 )

        store.clear()
        self.assertEquals( len( c.fetchall() ), 0 )

        os.unlink( dbref )


if __name__ == '__main__': unittest.main()


