# -*- coding: utf-8 -*-

from CodernityDB.database import Database
import CodernityDB
import logging


class DatabaseConnection:
    def __init__(self, path="./noSQLDB"):
        self.db = Database(path)

        try:
            self.db.create()
        except CodernityDB.index.IndexConflict:
            self.db.open()

        """
        print("********************************")
        print("FULL DB CONTENT:")
        print("********************************")
        for curr in self.db.all('id'):
            print curr
        print("********************************")
        """

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    dbConnection = DatabaseConnection()