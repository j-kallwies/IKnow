# -*- coding: utf-8 -*-

import logging

from PySide import QtGui
from PySide import QtCore

from ui.Ui_NewKnowledgeDialog import Ui_NewKnowledgeDialog


class NewKnowledgeDialog(QtGui.QDialog):
    def __init__(self, parent, tagModel, tagParentsModel, knowledgeModel, parentID=1, editRow=None):
        super(NewKnowledgeDialog, self).__init__(parent)
        self.ui = Ui_NewKnowledgeDialog()
        self.ui.setupUi(self)

        self.tagModel = tagModel
        self.tagParentsModel = tagParentsModel
        self.knowledgeModel = knowledgeModel

        self.ui.tagTreeWidget.setColumnWidth(0, 250)
        self.ui.tagTreeWidget.setColumnWidth(1, 20)

        if editRow is None:
            self.setWindowTitle("Add new piece of knowledge")
            self.ui.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
            self.ui.buttonBox.accepted.connect(self.addNewKnowledge)
            if parentID is not None:
                tagIDs = set([parentID])
            else:
                tagIDs = set()
            self.tagModel.fillTreeWidgetWithTags(self.ui.tagTreeWidget, checkable=True, IDstoCheck=tagIDs)
        else:
            self.setWindowTitle("Edit a piece of knowledge")
            self.ui.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Apply | QtGui.QDialogButtonBox.Reset)
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Reset).clicked.connect(self.resetDataFromModel)
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.updateModel)
            self.ui.buttonBox.accepted.connect(self.updateModelAndClose)

            self.knowledgeID = self.knowledgeModel.getIDByRow(editRow)
            logging.debug("self.knowledgeID=%s" % self.knowledgeID)
            self.editRow = editRow
            self.resetDataFromModel()
        self.ui.buttonBox.rejected.connect(self.close)

    def getSelectedTagIDs(self):
        logging.debug("topLevelItemCount()=%d" % self.ui.tagTreeWidget.topLevelItemCount())
        tagIDs = []
        for i in range(self.ui.tagTreeWidget.topLevelItemCount()):
            rootItem = self.ui.tagTreeWidget.topLevelItem(i)
            if rootItem.checkState(0) == 1:
                tagIDs.append(int(rootItem.data(1, 0)))
            tagIDs.extend(self.getSelectedTagIDsFromChilds(rootItem))
        return tagIDs

    def getSelectedTagIDsFromChilds(self, treeWidgetItem):
        tagIDs = []
        for i in range(treeWidgetItem.childCount()):
            childItem = treeWidgetItem.child(i)
            if childItem.checkState(0) == 1:
                tagIDs.append(int(childItem.data(1, 0)))
            tagIDs.extend(self.getSelectedTagIDsFromChilds(childItem))
        return tagIDs

    def resetDataFromModel(self):
        self.addTagsFromModel()

        data = self.knowledgeModel.getDataDictByID(self.knowledgeID)
        self.ui.tagNameEdit.setText(data["title"])
        self.ui.plainTextEdit.setPlainText(data["description"])

    def updateModel(self):
        logging.debug("updateModel")
        title = self.ui.tagNameEdit.text()
        description = self.ui.plainTextEdit.toPlainText()
        newTagIDs = self.getSelectedTagIDs()
        self.knowledgeModel.updateKnowledge(self.editRow, title, description, newTagIDs)

    def updateModelAndClose(self):
        self.updateModel()
        self.close()

    def addTagsFromModel(self):
        tagIDs = self.knowledgeModel.getTagIDsFromKnowledgeID(self.knowledgeID)
        print(tagIDs)
        self.tagModel.fillTreeWidgetWithTags(self.ui.tagTreeWidget, checkable=True, IDstoCheck=tagIDs)

    def addNewKnowledge(self):
        logging.debug("addNewKnowledge()")
        if self.ui.tagNameEdit.text() == "":
            return
        title = self.ui.tagNameEdit.text()
        description = self.ui.plainTextEdit.toPlainText()
        newKnowledgeID = self.knowledgeModel.addNewKnowledge(title, description)
        tagIDs = self.getSelectedTagIDs()
        logging.debug("getSelectedTagIDs()=%s" % str(tagIDs))
        for tagID in tagIDs:
            self.knowledgeModel.addTagForKnowledge(newKnowledgeID, tagID)
        self.close()

    def updateParentTagName(self, value):
        logging.debug("parentID=%d" % value)
        self.ui.parentTagLabel.setText(self.tagModel.getTagNameFromID(value))
