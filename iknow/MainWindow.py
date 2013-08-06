# -*- coding: utf-8 -*-

import logging

from PySide import QtGui
from PySide import QtCore

from ui.Ui_MainWindow import Ui_MainWindow
from NewTagDialog import NewTagDialog
from NewKnowledgeDialog import NewKnowledgeDialog
from tagModel import TagModel
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
        self.knowledgeModel = KnowledgeModel(self.dbConnection.db)

        # Setup views
        self.ui.knowledgeTableView.setModel(self.knowledgeModel)
        self.ui.knowledgeTableView.hideColumn(0)
        self.ui.knowledgeTableView.setColumnWidth(1, 600)
        self.ui.knowledgeTableView.setColumnWidth(2, 700)

        self.ui.tagTreeWidget.setColumnWidth(0, 300)
        self.ui.tagTreeWidget.setColumnWidth(1, 30)

        # Load tags
        self.updateTagWidget()

        self.currentTag = None

        # Create menus
        act = QtGui.QAction("Remove selected Tag", self, statusTip="Remove the selected Tag. The child Tags are not touched.", triggered=self.removeSelectedTag)
        self.ui.tagTreeWidget.addAction(act)
        self.ui.tagTreeWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        # Connect signals and slots
        self.ui.tagTreeWidget.currentItemChanged.connect(self.tagChanged)
        self.ui.newTagButton.clicked.connect(self.showNewTagButtonDialog)
        self.ui.updateTagsButton.clicked.connect(self.updateTagWidget)
        self.ui.newKnowledgeButton.clicked.connect(self.showNewKnowledgeDialog)

        self.ui.filterTagsEdit.textChanged.connect(self.updateTagWidget)

        self.ui.knowledgeTableView.doubleClicked.connect(self.showEditKnowledgeDialog)

    def removeSelectedTag(self):
        selectedItem = self.ui.tagTreeWidget.selectedItems()[0]
        IDtoRemove = int(selectedItem.text(1))
        logging.debug("Remove selected Tag (ID=%d)." % IDtoRemove)
        self.tagModel.removeTag(IDtoRemove)
        self.updateTagWidget()

    def updateTagWidget(self):
        logging.debug("filter-Edit=%s" % self.ui.filterTagsEdit.text())
        filter = self.ui.filterTagsEdit.text()
        if filter == "":
            filterIDs = None
        else:
            foundIDs = self.tagModel.getIDsFilteredByName(filter)
            logging.debug("foundIDs=" + str(foundIDs))
            filterIDs = []
            filterIDs.extend(foundIDs)
            for ID in foundIDs:
                logging.debug("foundIDs=%s" % str(foundIDs))
                filterIDs.extend(self.tagModel.getParentIDs(ID))
                filterIDs.extend(self.tagModel.getAllChildIDs(ID))
            filterIDs = set(filterIDs)
            logging.debug("filterIDs=" + str(filterIDs))
        self.tagModel.fillTreeWidgetWithTags(self.ui.tagTreeWidget, filterIDs=filterIDs)

        if self.ui.filterTagsEdit.text() is not "":
            self.ui.tagTreeWidget.expandAll()

    def showNewTagButtonDialog(self):
        logging.debug("Show NewTagDialog")
        newTagDlg = NewTagDialog(self, self.tagModel, self.tagModel.tagParentsModel, parentID=self.currentTag)
        newTagDlg.exec_()
        self.updateTagWidget()

    def showNewKnowledgeDialog(self):
        logging.debug("Show NewKnowledgeDialog")
        newKnowledgeDlg = NewKnowledgeDialog(self, self.tagModel, self.tagModel.tagParentsModel, self.knowledgeModel, parentID=self.currentTag)
        newKnowledgeDlg.exec_()
        self.knowledgeModel.setFilterByTagID(self.currentTag)

    def showEditKnowledgeDialog(self, modelIndex):
        logging.debug("Show EditKnowledgeDialog")
        logging.debug("Row=%d" % modelIndex.row())
        newKnowledgeDlg = NewKnowledgeDialog(self, self.tagModel, self.tagModel.tagParentsModel, self.knowledgeModel, editRow=modelIndex.row())
        newKnowledgeDlg.exec_()
        self.knowledgeModel.setFilterByTagID(self.currentTag)

    def tagChanged(self, current, previous):
        self.currentTag = int(current.text(1))
        self.knowledgeModel.setFilterByTagID(self.currentTag)

        logging.debug("currentTag = %d", self.currentTag)

