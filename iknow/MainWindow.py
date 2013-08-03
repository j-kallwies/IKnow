# -*- coding: utf-8 -*-

import logging

from PySide import QtGui
from PySide import QtCore

from ui.Ui_MainWindow import Ui_MainWindow
from tagModel import TagModel
from tagParentsModel import TagParentsModel
from knowledgeModel import KnowledgeModel
from databaseConnection import DatabaseConnection

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("IKnow")

        # DB-Connection
        self.dbConnection = DatabaseConnection()
        if self.dbConnection.connect():
            logging.info("Connected to the Database")
        else:
            logging.error("Failed to connect to the database")

        # Create Models
        self.tagModel = TagModel(self.dbConnection.db)
        self.tagParentsModel = TagParentsModel(self.dbConnection.db)
        self.knowledgeModel = KnowledgeModel(self.dbConnection.db)

        # Setup views
        self.ui.knowledgeTableView.setModel(self.knowledgeModel)
        self.ui.knowledgeTableView.hideColumn(0)
        self.ui.knowledgeTableView.setColumnWidth(1, 600)
        self.ui.knowledgeTableView.setColumnWidth(2, 700)

        # Insert root tags
        rootTags = self.getRootTags()
        self.ui.tagTreeWidget.clear()
        for rootID in sorted(rootTags.keys(), reverse=True):
            newElem = QtGui.QTreeWidgetItem([rootTags[rootID], str(rootID)])
            self.ui.tagTreeWidget.insertTopLevelItem(0, newElem)
            self.insertChildTags(rootID, newElem)

        self.tagParentsModel.setFilter("")
        self.tagParentsModel.select()

        self.ui.tagTreeWidget.currentItemChanged.connect(self.tagChanged)

    def tagChanged(self, current, previous):
        self.currentTag = int(current.text(1))
        self.knowledgeModel.setFilterByTagID(self.currentTag)

        logging.debug("currentTag = %d", self.currentTag)


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
        childTags = self.getChildTags(ID)
        logging.debug(self.getTagNameFromID(ID) + ": " + str(childTags))
        for childID in childTags.keys():
            newElem = QtGui.QTreeWidgetItem(treeWidgetItem, [self.getTagNameFromID(childID), str(childID)])
            if self.hasChildTags(childID):
                self.insertChildTags(childID, newElem)

    def getChildTags(self, ID):
        childTags = {}
        self.tagParentsModel.setFilter("parentTagID = %d" % ID)
        self.tagParentsModel.select()
        for i in range(self.tagParentsModel.rowCount()):
            ID = self.tagParentsModel.record(i).value("tagID")
            childTags[ID] = self.getTagNameFromID(ID)
        return childTags

    def hasChildTags(self, ID):
        self.tagParentsModel.setFilter("tagID = %d" % ID)
        self.tagParentsModel.select()
        return self.tagParentsModel.rowCount() > 0
