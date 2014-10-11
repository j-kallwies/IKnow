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

        # Create Models
        self.tagModel = TagModel(self.dbConnection)
        self.knowledgeModel = KnowledgeModel(self.dbConnection, self.tagModel)

        print("%d rows!" % self.knowledgeModel.rowCount())

        # Setup views
        self.ui.knowledgeTableView.setModel(self.knowledgeModel)
        #self.ui.knowledgeTableView.hideColumn(0)
        self.ui.knowledgeTableView.setColumnWidth(0, 300)
        self.ui.knowledgeTableView.setColumnWidth(1, 100)
        self.ui.knowledgeTableView.setColumnWidth(2, 300)
        self.ui.knowledgeTableView.setColumnWidth(3, 500)

        self.ui.tagTreeWidget.setColumnWidth(0, 300)
        self.ui.tagTreeWidget.setColumnWidth(1, 30)

        # Load tags
        self.updateTagWidget()

        self.currentTag = None
        self.filterKnowledgeText = ""

        # Create menus
        removeTagAction = QtGui.QAction("Remove selected Tag", self, statusTip="Remove the selected Tag. The child Tags are not touched.", triggered=self.removeSelectedTag)
        self.ui.tagTreeWidget.addAction(removeTagAction)
        self.ui.tagTreeWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        removeKnowledgeAction = QtGui.QAction("Remove selected knowledge", self, statusTip="Remove the selected piece of knowledge.", triggered=self.removeSelectedKnowledge)
        self.ui.knowledgeTableView.addAction(removeKnowledgeAction)
        self.ui.knowledgeTableView.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        # Connect signals and slots
        self.ui.tagTreeWidget.currentItemChanged.connect(self.tagChanged)
        self.ui.newTagButton.clicked.connect(self.showNewTagButtonDialog)
        self.ui.updateTagsButton.clicked.connect(self.updateTagWidget)
        self.ui.newKnowledgeButton.clicked.connect(self.showNewKnowledgeDialog)

        self.ui.filterTagsEdit.textChanged.connect(self.updateTagWidget)
        self.ui.filterKnowledgeEdit.textChanged.connect(self.filterKnowledgeByText)

        self.ui.knowledgeTableView.doubleClicked.connect(self.showEditKnowledgeDialog)

    def removeSelectedTag(self):
        selectedItem = self.ui.tagTreeWidget.selectedItems()[0]
        IDtoRemove = selectedItem.text(1)
        logging.debug("Remove selected Tag (ID=%s)." % IDtoRemove)
        self.tagModel.removeTag(IDtoRemove)
        self.updateTagWidget()

    def removeSelectedKnowledge(self):
        print("removeSelectedKnowledge")
        rowsToRemove = [index.row() for index in self.ui.knowledgeTableView.selectionModel().selectedRows()]
        print("Delete rows: %s" % rowsToRemove)
        self.knowledgeModel.removeRows(rowsToRemove)

    def updateTagWidget(self):
        self.tagModel.updateTree()

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
                filterIDs.extend(self.tagModel.getParentIDsDownToRoot(ID))
                filterIDs.extend(self.tagModel.getAllChildIDs(ID))
            filterIDs = set(filterIDs)
            logging.debug("filterIDs=" + str(filterIDs))

        # Clear tree
        self.ui.tagTreeWidget.clear()

        # No filter applied => Show all tags
        if filter == "":
            self.tagModel.fillTreeWidgetWithTags(self.ui.tagTreeWidget)

        # Found tags with applied filter
        if filter != "" and len(foundIDs) > 0:
            self.tagModel.fillTreeWidgetWithTags(self.ui.tagTreeWidget, filterIDs=filterIDs)
            self.ui.tagTreeWidget.expandAll()

    def showNewTagButtonDialog(self):
        logging.debug("Show NewTagDialog")
        newTagDlg = NewTagDialog(self, self.tagModel, self.tagModel.tagParentsModel, parentID=self.currentTag)
        newTagDlg.exec_()
        # TODO: Update only if tags really changed!
        self.updateTagWidget()

    def showNewKnowledgeDialog(self):
        logging.debug("Show NewKnowledgeDialog")
        newKnowledgeDlg = NewKnowledgeDialog(self, self.tagModel, self.tagModel.tagParentsModel, self.knowledgeModel, parentID=self.currentTag)
        newKnowledgeDlg.exec_()
        self.reloadKnowledge()

    def showEditKnowledgeDialog(self, modelIndex):
        logging.debug("Show EditKnowledgeDialog")
        logging.debug("Row=%d" % modelIndex.row())
        newKnowledgeDlg = NewKnowledgeDialog(self, self.tagModel, self.tagModel.tagParentsModel, self.knowledgeModel, editRow=modelIndex.row())
        newKnowledgeDlg.exec_()
        self.knowledgeModel.setFilterByTagID(self.currentTag)

    def tagChanged(self, current, previous):
        self.currentTag = str(current.text(1))
        logging.debug("currentTag = %s", self.currentTag)
        self.reloadKnowledge()

    def filterKnowledgeByText(self, filterText):
        self.filterKnowledgeText = str(filterText)
        logging.debug("filterKnowledgeByText: self.filterKnowledgeText=%s" % self.filterKnowledgeText)
        self.reloadKnowledge()

    def reloadKnowledge(self):
        self.knowledgeModel.reload(self.currentTag, self.filterKnowledgeText)
