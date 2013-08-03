import logging

from PySide import QtSql


class KnowledgeTagsModel(QtSql.QSqlTableModel):
    def __init__(self, db):
        super(KnowledgeTagsModel, self).__init__(None, db)
        self.setTable("knowledge_tags")
        self.select()
        logging.debug("%d rows in KnowledgeTagsModel" % self.rowCount())

    def getKnowledgeIDsFromTagID(self, tagID):
        self.setFilter("tag_ID=%d" % tagID)
        self.select()
        knowledgeIDs = []
        for i in range(self.rowCount()):
            knowledgeIDs.append(self.record(i).value("knowledge_ID"))
        return knowledgeIDs


class KnowledgeModel(QtSql.QSqlTableModel):
    def __init__(self, db):
        super(KnowledgeModel, self).__init__(None, db)
        self.setTable("knowledge")
        self.select()
        logging.debug("%d rows in KnowledgeModel" % self.rowCount())

        self.knowledgeTagsModel = KnowledgeTagsModel(db)

    def setFilterByTagID(self, tagID):
        knowledgeIDs = self.knowledgeTagsModel.getKnowledgeIDsFromTagID(tagID)
        logging.debug("getKnowledgeIDsFromTagID(%d)=%s" % (tagID, str(knowledgeIDs)))
        if len(knowledgeIDs) == 0:
            filter = "False"
        else:
            filter = "ID=%d" % knowledgeIDs[0]
            if len(knowledgeIDs) > 1:
                for knowledgeID in knowledgeIDs[1:]:
                    filter = filter + " OR ID=%d" % knowledgeID

        logging.debug("filter=%s" % filter)
        self.setFilter(filter)
        self.select()
