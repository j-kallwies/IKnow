import logging

from PySide import QtSql
from PySide import QtCore
from PySide.QtCore import QModelIndex

class TagModel(QtSql.QSqlRelationalTableModel):
    def __init__(self, db):
        super(TagModel, self).__init__(None, db)
        self.setTable("tags")
        self.select()
        logging.debug("%d rows in TagModel" % self.rowCount())

    def addTag(self, name):
        self.setFilter("")
        self.setSort(0, QtCore.Qt.SortOrder.DescendingOrder)
        self.select()

        self.setSort(0, QtCore.Qt.SortOrder.AscendingOrder)

    def addTag(self, name):
        self.setFilter("")
        self.setSort(0, QtCore.Qt.SortOrder.AscendingOrder)
        self.select()

        record = QtSql.QSqlRecord()
        record.append(QtSql.QSqlField("ID"))
        record.append(QtSql.QSqlField("name"))
        record.setValue(1, name)
        if not self.insertRecord(self.rowCount()-1, record):
            raise "Tag could not be inserted."
        newID = int(self.record(self.rowCount()-1).value(0))
        logging.debug("newID=%d" % newID)

        return newID

    def removeTag(self, ID):
        self.setFilter("ID=%d" % ID)
        self.select()
        logging.debug("removeTag: self.rowCount()=%d" % self.rowCount())
        if self.rowCount() == 1:
            self.removeRow(0)

    def getTagNameFromID(self, ID):
        self.setFilter("ID=%d" % ID)
        self.select()
        if self.rowCount() == 1:
            return self.record(0).value("name")

    def hasID(self, ID):
        self.setFilter("ID=%d" % ID)
        self.select()
        return self.rowCount() == 1
