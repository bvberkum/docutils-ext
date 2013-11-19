"""
mpe extractor/storage 'LogBook'

Use case: a log book is a frequently updated document or set of documents,
    wherein discrete parts represent specific periods of time and the
    items therein are interpreted according to some set of rules.

    The transform should/could be used in combination with the rSt writer 
    to keep log books in a certain format, ie. reformatting then but also indexing
    and resolving references upon incrementing to a new log period.

Initial specs:
    - period interval is fixed to day.
    - one document maps to one period.
    - TODO: document should get datetime title
    - TODO: create tag index documents; perhaps load indices into SQL db..

Schema and other notes in journal.
        
"""
from nabu import extract
from dotmpe.du.ext import extractor


class LogBookExtractor(extract.Extractor):

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


class LogBookStorage(extractor.SQLiteExtractorStorage):

    sql_relations_unid = [
        ('logbook', 'TABLE', '''

            CREATE TABLE logbook
            (
               unid VARCHAR PRIMARY KEY,
               title VARCHAR,
               -- The period entries encompass
               date_start DATE,
               date_end DATE,
               -- Location is the netpath without domain.
               location VARCHAR,
               entry_count INT

               -- Disclosure is
               --  0: public
               --  1: shared
               --  2: private
               disclosure INT DEFAULT 2,
            )

        '''),

        ('logbook_entry', 'TABLE', '''

            CREATE TABLE logbook_entry
            (
               unid VARCHAR PRIMARY KEY,
               date DATE NOT NULL,
               blockitem_count INT DEFAULT '0',
               finalized BOOL DEFAULT FALSE,
               logbook_id VARCHAR
            )

        '''),

        ('logbook_blockitem', 'TABLE', '''

            CREATE TABLE logbook_blockitem
            (
               unid VARCHAR PRIMARY KEY,
            )

        '''),

        ('logbook_topic', 'TABLE', '''

            CREATE TABLE logbook_topic
            (
               unid VARCHAR PRIMARY KEY,
               tags VARCHAR
            )

        '''),

        ('logbook_tag', 'TABLE', '''

            CREATE TABLE logbook_tag
            (
               unid VARCHAR PRIMARY KEY,
               label VARCHAR NOT NULL
            )

        '''),
        ]

    sql_relations = [
        ('tagindex_idx', 'INDEX',
         """CREATE INDEX logbook_tag_idx ON logbook_tag (label)""")
        ]

    def __init__(self, *args, **kwds):
        extractor.SQLiteExtractorStorage.__init__(self, *args, **kwds)

    def store(self, source_id, *args):
        pass

    def clear(self, source_id):
        pass

#    def reset_schema(self, source_id):
#        raise NotImplemented


Extractor = LogBookExtractor
Storage = LogBookStorage

