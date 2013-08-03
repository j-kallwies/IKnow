# -*- coding: utf-8 -*-

from PySide import QtSql
import logging


class DatabaseConnection:
    def __init__(self, databaseName="./IKnow.sqlite", driver="QSQLITE"):
        self.db = QtSql.QSqlDatabase(driver)
        self.db.setDatabaseName(databaseName)

    def connect(self, userName="", password=""):
        status = self.db.open(userName, password)
        if status is not True:
            sqlError = self.db.lastError()
            logging.critical("Could not connect to the Database: %d %s " % (sqlError.number(), sqlError.text()))
        else:
            logging.info("Connected to SQLite-DB")
            logging.debug("db.tables()=%s" % str(self.db.tables()))

        return status

    def exececute(self, query):
        q = QtSql.QSqlQuery(self.db)
        return q.exec_(query)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    dbConnection = DatabaseConnection()
    dbConnection.connect()
