import logging

from PySide import QtCore

from tagModel import getFilterFromIDs, TagModel

"""
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
"""


class KnowledgeModel(QtCore.QAbstractTableModel):
    def __init__(self, db):
        super(KnowledgeModel, self).__init__()

        self.db = db

        self.tagModel = TagModel(db)

        self._filterByTagIDs = set()

        self.columns = ["_id", "_rev", "title", "description"]

        self.update()

        # TODO: Load rows before!
        logging.debug("%d rows in KnowledgeModel" % self.rowCount())

    def update(self):
        print("update()")
        self._data = []
        for curr in self.db.all('id'):
            if curr["_t"] == "knowledge":
                tags = set(curr["tags"])
                print("***DATA***: %s" % str(curr))

                if len(self._filterByTagIDs) > 0 and len(tags & self._filterByTagIDs) == 0:
                    continue

                self._data.append(curr)

        topLeft = self.index(0, 0);
        bottomRight = self.index(self.rowCount() - 1, self.columnCount() - 1)

        self.dataChanged.emit(topLeft, bottomRight) # TODO: Do it only if data really changed
        self.layoutChanged.emit() # TODO: Do it only if row- or column-count changed

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.columns)

    def getDataDictByID(self, ID):
        for data in self._data:
            if data["_id"] == ID:
                return data

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = self.columns[index.column()]
            return self._data[row][col]
        else:
            return None

    def getIDByRow(self, row):
        return self._data[row]["_id"]

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """ Set the headers to be displayed. """
        if role != QtCore.Qt.DisplayRole:
            return None

        if orientation == QtCore.Qt.Horizontal:
            if section < len(self.columns):
                return self.columns[section]
            else:
                return str(section)

        return None

    def setFilterByTagID(self, tagID):
        pass

    def addNewKnowledge(self, title, description, tags):
        newData = {"_t": "knowledge", "title": title, "description": description, "tags": tags}
        res = self.db.insert(newData)

        self.update()

        return res['_id']

    def updateKnowledge(self, ID, title, description, newTagIDs):
        data = self.getDataDictByID(ID)
        assert data is not None, 'The knowledge with the ID "%s" was not found!' % str(ID)
        data["title"] = title
        data["description"] = description
        data["tags"] = newTagIDs
        self.db.update(data)

    def removeTagFromKnowledge(self, knowledgeID, tagID):
        pass
        """
        self.knowledgeTagsModel.removeTagFromKnowledge(knowledgeID, tagID)
        """

    def addTagForKnowledge(self, knowledgeID, tagID):
        pass
        """
        self.knowledgeTagsModel.addTagForKnowledge(knowledgeID, tagID)
        """

    def getTagIDsFromKnowledgeID(self, knowledgeID):
        if "tags" in self.getDataDictByID(knowledgeID):
            return self.getDataDictByID(knowledgeID)["tags"]
        else:
            return []

    def reload(self, currentTag=None, filterText=None):
        if currentTag is not None:
            tagIDs = [currentTag]
            tagIDs.extend(self.tagModel.getAllChildIDs(currentTag))
        else:
            tagIDs = []
        logging.debug("reload(): tagIDs = %s" % str(tagIDs))
        self._filterByTagIDs = set(tagIDs)
        self._filterByText = filterText
        self.update()
