# -*- coding: utf-8 -*-

import logging

from PySide import QtGui
from PySide import QtCore

from ui.Ui_MainWindow import Ui_MainWindow
from NewTagDialog import NewTagDialog
from NewKnowledgeDialog import NewKnowledgeDialog
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

        # Load tags
        self.updateTagWidget()

        self.currentTag = None

        # Connect signals and slots
        self.ui.tagTreeWidget.currentItemChanged.connect(self.tagChanged)
        self.ui.newTagButton.clicked.connect(self.showNewTagButtonDialog)
        self.ui.updateTagsButton.clicked.connect(self.updateTagWidget)
        self.ui.newKnowledgeButton.clicked.connect(self.showNewKnowledgeDialog)

    def updateTagWidget(self):
        # Insert root tags
        rootTags = self.getRootTags()
        self.ui.tagTreeWidget.clear()
        for rootID in sorted(rootTags.keys(), reverse=True):
            newElem = QtGui.QTreeWidgetItem([rootTags[rootID], str(rootID)])
            self.ui.tagTreeWidget.insertTopLevelItem(0, newElem)
            self.insertChildTags(rootID, newElem)

    def showNewTagButtonDialog(self):
        logging.debug("Show NewTagDialog")
        newTagDlg = NewTagDialog(self, self.tagModel, self.tagParentsModel, parentID=self.currentTag)
        newTagDlg.exec_()
        self.updateTagWidget()

    def showNewKnowledgeDialog(self):
        logging.debug("Show NewKnowledgeDialog")
        newKnowledgeDlg = NewKnowledgeDialog(self, self.tagModel, self.tagParentsModel, self.knowledgeModel, parentID=self.currentTag)
        newKnowledgeDlg.exec_()
        self.knowledgeModel.setFilterByTagID(self.currentTag)

    def tagChanged(self, current, previous):
        self.currentTag = int(current.text(1))
        self.knowledgeModel.setFilterByTagID(self.currentTag)

        logging.debug("currentTag = %d", self.currentTag)

    def getRootTags(self):
        self.tagModel.setFilter("")
        self.tagModel.select()
        self.tagParentsModel.setFilter("")
        self.tagParentsModel.select()
        rootTags = {}
        for i in range(self.tagModel.rowCount()):
            ID = self.tagModel.record(i).value("ID")
            tag = self.tagModel.record(i).value("name")
            if not self.hasChildTags(ID):
                rootTags[ID] = tag
        return rootTags

    def insertChildTags(self, ID, treeWidgetItem):
        if not self.tagModel.hasID(ID):
            return

        childTags = self.getChildTags(ID)
        logging.debug(self.tagModel.getTagNameFromID(ID) + ": " + str(childTags))
        for childID in childTags.keys():
            if self.tagModel.hasID(childID):
                newElem = QtGui.QTreeWidgetItem(treeWidgetItem, [self.tagModel.getTagNameFromID(childID), str(childID)])
                if self.hasChildTags(childID):
                    self.insertChildTags(childID, newElem)

    def getChildTags(self, ID):
        childTags = {}
        self.tagParentsModel.setFilter("parentTagID = %d" % ID)
        self.tagParentsModel.select()
        for i in range(self.tagParentsModel.rowCount()):
            ID = self.tagParentsModel.record(i).value("tagID")
            childTags[ID] = self.tagModel.getTagNameFromID(ID)
        return childTags

    def hasChildTags(self, ID):
        self.tagParentsModel.setFilter("tagID = %d" % ID)
        self.tagParentsModel.select()
        return self.tagParentsModel.rowCount() > 0
