import logging

from PySide import QtSql

class TagModel(QtSql.QSqlRelationalTableModel):
    def __init__(self, db):
        super(TagModel, self).__init__(None, db)
        self.setTable("tags")
        self.select()
        logging.debug("%d rows in TagModel" % self.rowCount())
