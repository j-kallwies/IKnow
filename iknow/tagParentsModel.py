import logging

from PySide import QtSql

class TagParentsModel(QtSql.QSqlRelationalTableModel):
    def __init__(self, db):
        super(TagParentsModel, self).__init__(None, db)
        self.setTable("tag_parents")
        self.select()
        logging.debug("%d rows in TagParentsModel" % self.rowCount())