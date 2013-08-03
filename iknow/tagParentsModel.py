import logging

from PySide import QtSql

class TagParentsModel(QtSql.QSqlRelationalTableModel):
    def __init__(self, db):
        super(TagParentsModel, self).__init__(None, db)
        self.setTable("tag_parents")
        self.select()
        logging.debug("%d rows in TagParentsModel" % self.rowCount())

    def addParentTag(self, tagID, parentTagID):
        record = QtSql.QSqlRecord()
        record.append(QtSql.QSqlField("ID"))
        record.append(QtSql.QSqlField("tagID"))
        record.append(QtSql.QSqlField("parentTagID"))
        record.setValue(1, tagID)
        record.setValue(2, parentTagID)
        return self.insertRecord(self.rowCount()-1, record)
