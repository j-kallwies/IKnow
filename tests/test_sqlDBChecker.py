import context
import logging

from PySide import QtSql

from iknow.databaseConnection import DatabaseConnection
from iknow.sqlDBChecker import SqlDBChecker


databaseStructure1 = {"knowledge": [{"fieldName": "ID", "type": "INDEX"},
                                    {"fieldName": "title", "type": "VARCHAR"},
                                    {"fieldName": "description", "type": "TEXT", "mayBeZero": True},
                                    {"fieldName": "author", "type": "VARCHAR", "default": "jan"},
                                    {"fieldName": "created", "type": "DATETIME", "mayBeZero": True}]
                      }


databaseStructure2 = {"knowledge": [{"fieldName": "ID", "type": "INDEX"},
                                    {"fieldName": "title", "type": "VARCHAR"},
                                    {"fieldName": "description", "type": "TEXT", "mayBeZero": True},
                                    {"fieldName": "author", "type": "VARCHAR", "default": "jan"},
                                    {"fieldName": "created", "type": "DATETIME", "mayBeZero": True}],
                      "foo": [{"fieldName": "ID", "type": "INDEX"},
                              {"fieldName": "bar", "type": "VARCHAR"}]
                      }


createKnowledgeSQL = '''CREATE TABLE "knowledge" ("ID" INTEGER PRIMARY KEY NOT NULL UNIQUE,
                        "title" VARCHAR NOT NULL,
                        "description" TEXT,
                        "author" VARCHAR NOT NULL,
                        "created" DATETIME);'''


createIncompleteKnowledgeSQL = '''CREATE TABLE "knowledge" ("ID" INTEGER PRIMARY KEY NOT NULL UNIQUE,
                                  "description" TEXT);'''


class TestSqlDBChecker:
    def connectToDB(self):
        self.dbConnection = DatabaseConnection(databaseName=":memory:", driver="QSQLITE")
        self.dbConnection.connect()

    def init1(self):
        self.connectToDB()

        query = QtSql.QSqlQuery(self.dbConnection.db)
        query.exec_(createKnowledgeSQL)

        self.createSqlChecker()

    def init2(self):
        self.connectToDB()

        query = QtSql.QSqlQuery(self.dbConnection.db)
        query.exec_(createIncompleteKnowledgeSQL)

        self.createSqlChecker()

    def createSqlChecker(self):
        self.sqlDBChecker1 = SqlDBChecker(self.dbConnection.db, databaseStructure1)
        self.sqlDBChecker2 = SqlDBChecker(self.dbConnection.db, databaseStructure2)

    def test_tablesComplete(self):
        self.init1()
        assert self.sqlDBChecker1.tablesComplete() is True
        assert self.sqlDBChecker2.tablesComplete() is False

        self.sqlDBChecker2.createTable("foo")
        assert self.sqlDBChecker2.tablesComplete() is True

    def test_tableFieldsComplete(self):
        # Init with complete knowledge table
        self.init1()

        assert self.sqlDBChecker1.tableFieldsComplete("knowledge") is True
        self.sqlDBChecker1.repairTable("knowledge")

        assert self.sqlDBChecker1.tableFieldsComplete("knowledge") is True

        # Init with incomplete knowledge table
        self.init2()
        assert self.sqlDBChecker1.tableFieldsComplete("knowledge") is False

        self.sqlDBChecker1.repairTable("knowledge")

        assert self.sqlDBChecker1.tableFieldsComplete("knowledge") is True

    def test_SqlQueryForField(self):
        self.init1()
        assert self.sqlDBChecker1.sqlQueryForField("knowledge", "ID") == '"ID" INTEGER PRIMARY KEY NOT NULL UNIQUE'
        assert self.sqlDBChecker1.sqlQueryForField("knowledge", "title") == '"title" VARCHAR NOT NULL DEFAULT ""'
        assert self.sqlDBChecker1.sqlQueryForField("knowledge", "description") == '"description" TEXT'
        assert self.sqlDBChecker1.sqlQueryForField("knowledge", "author") == '"author" VARCHAR NOT NULL DEFAULT "jan"'
        assert self.sqlDBChecker1.sqlQueryForField("knowledge", "created") == '"created" DATETIME'

    def test_sqlCreateTable(self):
        self.init1()
        assert self.sqlDBChecker1.sqlCreateTable("knowledge") == 'CREATE TABLE "knowledge" ("ID" INTEGER PRIMARY KEY NOT NULL UNIQUE, "title" VARCHAR NOT NULL DEFAULT "", "description" TEXT, "author" VARCHAR NOT NULL DEFAULT "jan", "created" DATETIME);'
