import logging

from PySide import QtCore
from PySide import QtSql

from tagModel import getFilterFromIDs, TagModel


class KnowledgeTagsModel(QtSql.QSqlTableModel):
    def __init__(self, db):
        super(KnowledgeTagsModel, self).__init__(None, db)
        self.setTable("knowledge_tags")
        self.select()
        logging.debug("%d rows in KnowledgeTagsModel" % self.rowCount())

    def getKnowledgeIDsFromTagIDs(self, tagIDs):
        self.setFilter(getFilterFromIDs(tagIDs, "tag_ID"))
        self.select()
        knowledgeIDs = []
        for i in range(self.rowCount()):
            knowledgeIDs.append(self.record(i).value("knowledge_ID"))
        return knowledgeIDs

    def getTagIDsFromKnowledgeID(self, knowledgeID):
        self.setFilter("knowledge_ID=%d" % knowledgeID)
        self.select()
        tagIDs = []
        for i in range(self.rowCount()):
            tagIDs.append(self.record(i).value("tag_ID"))
        return tagIDs

    def addTagForKnowledge(self, knowledgeID, tagID):
        logging.debug("Adding tagID %d for knowledgeID %d" % (tagID, knowledgeID))
        record = QtSql.QSqlRecord()
        record.append(QtSql.QSqlField("ID"))
        record.append(QtSql.QSqlField("knowledge_ID"))
        record.append(QtSql.QSqlField("tag_ID"))
        record.setValue(1, knowledgeID)
        record.setValue(2, tagID)
        return self.insertRecord(self.rowCount() - 1, record)

    def removeTagFromKnowledge(self, knowledgeID, tagID):
        self.setFilter("knowledge_ID=%d AND tag_ID=%d" % (knowledgeID, tagID))
        self.select()
        while self.rowCount() > 0:
            logging.debug("Removing tagID %d from knowledgeID %d" % (tagID, knowledgeID))
            self.removeRow(0)


class KnowledgeModel(QtSql.QSqlTableModel):
    def __init__(self, db):
        super(KnowledgeModel, self).__init__(None, db)
        self.setTable("knowledge")
        self.select()
        logging.debug("%d rows in KnowledgeModel" % self.rowCount())

        self.knowledgeTagsModel = KnowledgeTagsModel(db)
        self.tagModel = TagModel(db)

    def setFilterByTagIDsAndText(self, tagIDs, filterText):
        if len(tagIDs) == 0:
            filterByTags = "1"
        else:
            knowledgeIDs = self.knowledgeTagsModel.getKnowledgeIDsFromTagIDs(tagIDs)
            logging.debug("getKnowledgeIDsFromTagIDs(%s)=%s" % (str(tagIDs), str(knowledgeIDs)))
            if len(knowledgeIDs) == 0:
                filterByTags = "0"
            else:
                filterByTags = getFilterFromIDs(knowledgeIDs, "ID")

        if filterText is not None and filterText != "":
            filterByText = '(title LIKE "%' + filterText + '%") OR (description LIKE "%' + filterText + '%")'
        else:
            filterByText = ''

        logging.debug('filterByTags="%s"' % filterByTags)
        logging.debug('filterByText="%s"' % filterByText)
        if filterByText != "":
            self.setFilter("(%s) AND (%s)" % (filterByTags, filterByText))
        else:
            self.setFilter(filterByTags)
        logging.debug('knowledgeModel.filter = "%s"' % self.filter())
        self.select()

    def addNewKnowledge(self, title, description):
        self.setFilter("")
        self.setSort(0, QtCore.Qt.SortOrder.AscendingOrder)
        self.select()

        record = QtSql.QSqlRecord()
        record.append(QtSql.QSqlField("ID"))
        record.append(QtSql.QSqlField("title"))
        record.append(QtSql.QSqlField("description"))
        record.append(QtSql.QSqlField("author"))
        record.setValue(1, title)
        record.setValue(2, description)
        record.setValue(3, "jan")
        if not self.insertRecord(self.rowCount() - 1, record):
            raise "Knowledge could not be inserted."
        return int(self.record(self.rowCount() - 1).value(0))

    def updateKnowledge(self, row, title, description, newTagIDs):
        knowledgeID = self.record(row).value("ID")

        self.setData(self.index(row, self.fieldIndex("title")), title)
        self.setData(self.index(row, self.fieldIndex("description")), description)
        self.submitAll()

        logging.debug("updateKnowledge: knowledgeID=%d" % knowledgeID)

        oldTagIds = set(self.getTagIDsFromKnowledgeID(knowledgeID))
        newTagIDs = set(newTagIDs)

        tagIDsToAdd = newTagIDs - oldTagIds
        tagIDsToRemove = oldTagIds - newTagIDs

        logging.debug("OldTagIDs: %s" % str(oldTagIds))
        logging.debug("NewTagIDs: %s" % str(newTagIDs))

        logging.debug("TagIDsToAdd: %s" % str(tagIDsToAdd))
        logging.debug("TagIDsToRemove: %s" % str(tagIDsToRemove))

        for tagID in tagIDsToAdd:
            self.addTagForKnowledge(knowledgeID, tagID)

        for tagID in tagIDsToRemove:
            self.removeTagFromKnowledge(knowledgeID, tagID)

    def removeTagFromKnowledge(self, knowledgeID, tagID):
        self.knowledgeTagsModel.removeTagFromKnowledge(knowledgeID, tagID)

    def addTagForKnowledge(self, knowledgeID, tagID):
        self.knowledgeTagsModel.addTagForKnowledge(knowledgeID, tagID)

    def getTagIDsFromKnowledgeID(self, knowledgeID):
        return self.knowledgeTagsModel.getTagIDsFromKnowledgeID(knowledgeID)

    def reload(self, currentTag=None, filterText=None):
        if currentTag is not None:
            tagIDs = [currentTag]
            tagIDs.extend(self.tagModel.getAllChildIDs(currentTag))
        else:
            tagIDs = []
        logging.debug("reload(): tagIDs = %s" % str(tagIDs))
        self.setFilterByTagIDsAndText(tagIDs, filterText)
        self.select()
