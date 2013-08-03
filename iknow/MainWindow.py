# -*- coding: utf-8 -*-

import logging

from PySide import QtGui

from ui.Ui_MainWindow import Ui_MainWindow
from tagModel import TagModel
from tagParentsModel import TagParentsModel
from databaseConnection import DatabaseConnection

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # DB-Connection
        self.dbConnection = DatabaseConnection()
        if self.dbConnection.connect():
            logging.info("Connected to the Database")
        else:
            logging.error("Failed to connect to the database")

        #Create Models
        self.tagModel = TagModel(self.dbConnection.db)
        self.ui.tableView.setModel(self.tagModel)
        self.tagParentsModel = TagParentsModel(self.dbConnection.db)
        self.ui.tableView_2.setModel(self.tagParentsModel)

        rootTags = self.getRootTags()

        print(rootTags)

        self.ui.tagTreeWidget.clear()
        for rootID in sorted(rootTags.keys(), reverse=True):
            elem = QtGui.QTreeWidgetItem([str(rootID), rootTags[rootID]])
            self.ui.tagTreeWidget.insertTopLevelItem(0, elem)

        self.tagParentsModel.setFilter("")
        self.tagParentsModel.select()

        print("Children of Ingw.: "+str(self.getChildTags(28)))

        self.setWindowTitle("IKnow")

    def getRootTags(self):
        rootTags = {}
        for i in range(self.tagModel.rowCount()):
            ID = self.tagModel.record(i).value("ID")
            tag = self.tagModel.record(i).value("name")
            if not self.hasChildTags(ID):
                rootTags[ID] = tag
        return rootTags

    def getTagNameFromID(self, ID):
        self.tagModel.setFilter("ID=%d" % ID)
        self.tagModel.select()
        if self.tagModel.rowCount() == 1:
            return self.tagModel.record(0).value("name")

    def insertChildTags(self, ID, treeWidgetItem):
        self.tagParentsModel.getChildList(ID)

    def getChildTags(self, ID):
        childTags = {}
        self.tagParentsModel.setFilter("parentTagID = %d" % ID)
        self.tagParentsModel.select()
        print("tagParentsModel.count()=%d" % self.tagParentsModel.rowCount())
        for i in range(self.tagParentsModel.rowCount()):
            ID = self.tagParentsModel.record(i).value("tagID")
            childTags[ID] = self.getTagNameFromID(ID)
        return childTags

    def hasChildTags(self, ID):
        self.tagParentsModel.setFilter("tagID = %d" % ID)
        self.tagParentsModel.select()
        return self.tagParentsModel.rowCount() > 0
