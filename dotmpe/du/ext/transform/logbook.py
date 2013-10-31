"""
mpe Transform 'LogBook'

For documentation see Extractor 'LogBook'.


"""
from docutils import transforms, nodes
import sqlite3

from dotmpe.du import util
from dotmpe.du.ext.extractor import logbook


logger = util.get_log(__name__)

class LogBook(transforms.Transform):

    settings_spec = (
            )

    default_priority = 900

    def apply(self):
        logger.warning('Running LogBook xform')
        doc = self.document

        connection = sqlite3.connect(doc.settings.logbook_db)
        store = logbook.Storage(None, connection)
        logger.debug(store)

        terms = doc.traverse(nodes.term)
        for e in terms:
            tags = e.astext().split(' ')
            logger.warn(e)

#        terms = doc.traverse(nodes.definition)
#        for e in terms:
#            logger.warn(e)

#        topics = doc.traverse(nodes.definition_list)
#        for e in topics:
#            logger.warn(e)

#        topicblocks = doc.traverse(nodes.definition_list_item)
#        for e in topicblocks:
#            logger.warn(e)

        # add date to title
        #self.document
        connection.close()

#    class Visitor(


