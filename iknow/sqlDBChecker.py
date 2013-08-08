import logging
from PySide import QtSql

logging.basicConfig(level=logging.DEBUG)


class SqlDBChecker:
    def __init__(self, db, dbStructure):
        self.db = db
        self.dbStructure = dbStructure

    def _execSQL(self, query):
        q = QtSql.QSqlQuery(self.db)
        return q.exec_(query)

    def tables(self):
        return self.db.tables()

    def tableFields(self, tableName):
        result = []
        fields = self.db.record(tableName)
        for i in range(fields.count()):
            result.append(fields.field(i))
        return result

    def tableFieldNames(self, tableName):
        result = []
        for i in self.tableFields(tableName):
            result.append(i.name())
        return result

    def tablesComplete(self):
        neededTables = set(self.dbStructure.keys())
        return len(neededTables - set(self.tables())) == 0

    def getDefindedFieldNames(self, tableName):
        return set([field["fieldName"] for field in self.dbStructure[tableName]])

    def tableFieldsComplete(self, tableName):
        missingFields = self.getMissingFields(tableName)
        print("missingFields=%s" % str(missingFields))
        return len(missingFields) == 0

    def sqlCreateTable(self, tableName):
        if self.db.driverName() == "QSQLITE":
            fieldQueries = [self.sqlQueryForField(tableName, field["fieldName"]) for field in self.dbStructure[tableName]]
            return 'CREATE TABLE "%s" (%s);' % (tableName, ", ".join(fieldQueries))

    def getSqlType(self, typeName):
        if self.db.driverName() == "QSQLITE":
            map = {"INDEX": 'INTEGER PRIMARY KEY NOT NULL UNIQUE'}
        if typeName in map:
            return map[typeName]
        else:
            return typeName

    def getField(self, tableName, fieldName):
        table = self.dbStructure[tableName]
        for field in table:
            if field["fieldName"] == fieldName:
                return field

    def sqlQueryForField(self, tableName, fieldName):
        if self.db.driverName() == "QSQLITE":
            field = self.getField(tableName, fieldName)

            if "mayBeZero" in field:
                mayBeZero = field["mayBeZero"]
            elif field["type"] == "INDEX":
                mayBeZero = True
            else:
                mayBeZero = False

            mayBeZeroSql = {True: "", False: " NOT NULL"}

            if "default" in field:
                defaultValue = field["default"]
            else:
                defaultValue = ""

            return '"%s" %s%s%s' % (fieldName, self.getSqlType(field["type"]), mayBeZeroSql[mayBeZero], "" if mayBeZero else ' DEFAULT "%s"' % defaultValue)

    def insertField(self, tableName, fieldName):
        if self.db.driverName() == "QSQLITE":
            self._execSQL('ALTER TABLE "%s" ADD COLUMN %s;' % (tableName, self.sqlQueryForField(tableName, fieldName)))

    def createTable(self, tableName):
        self._execSQL(self.sqlCreateTable(tableName))

    def getMissingFields(self, tableName):
        return self.getDefindedFieldNames(tableName) - set(self.tableFieldNames(tableName))

    def repairTable(self, tableName):
        missingFields = self.getMissingFields(tableName)
        if len(missingFields) == 0:
            return
        for newFieldName in missingFields:
            self.insertField(tableName, newFieldName)
