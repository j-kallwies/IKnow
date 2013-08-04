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


        self.ui.assignedTagsList.setColumnWidth(0, 35)
        self.ui.assignedTagsList.setColumnWidth(1, 240)

        if editRow is None:
            self.setWindowTitle("Add new piece of knowledge")
            self.ui.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
            self.ui.buttonBox.accepted.connect(self.addNewKnowledge)
            if parentID is not None:
                self.ui.newTagSpinBox.setValue(parentID)
                self.updateParentTagName(parentID)
                self.addTagFromSpinbox()
        else:
            self.setWindowTitle("Edit a piece of knowledge")
            self.ui.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Apply | QtGui.QDialogButtonBox.Reset)
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Reset).clicked.connect(self.resetDataFromModel)
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.updateModel)
            self.ui.buttonBox.accepted.connect(self.updateModelAndClose)

            self.knowledgeID = self.knowledgeModel.record(editRow).value("ID")
            logging.debug("self.knowledgeID=%d" % self.knowledgeID)
            self.editRow = editRow
            self.resetDataFromModel()

        self.ui.newTagSpinBox.valueChanged.connect(self.updateParentTagName)
        self.ui.buttonBox.rejected.connect(self.close)
        self.ui.addTagButton.clicked.connect(self.addTagFromSpinbox)
        self.ui.removeTagButton.clicked.connect(self.removeTag)

        #self.ui.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)

    def resetDataFromModel(self):
        self.clearTags()
        self.addTagsFromModel()

        title = self.knowledgeModel.record(self.editRow).value("title")
        description = self.knowledgeModel.record(self.editRow).value("description")
        self.ui.tagNameEdit.setText(title)
        self.ui.plainTextEdit.setPlainText(description)

    def updateModel(self):
        logging.debug("updateModel")
        title = self.ui.tagNameEdit.text()
        description = self.ui.plainTextEdit.toPlainText()
        newTagIDs = [int(self.ui.assignedTagsList.item(i,0).data(0)) for i in range(self.ui.assignedTagsList.rowCount())]
        self.knowledgeModel.updateKnowledge(self.editRow, title, description, newTagIDs)

    def updateModelAndClose(self):
        self.updateModel()
        self.close()

    def clearTags(self):
        while self.ui.assignedTagsList.rowCount() > 0:
            self.ui.assignedTagsList.removeRow(0)

    def addTagsFromModel(self):
        tagIDs = self.knowledgeModel.getTagIDsFromKnowledgeID(self.knowledgeID)
        logging.debug("getTagIDsFromKnowledgeID=%s" % str(tagIDs))
        for tagID in tagIDs:
            self.addTag(tagID)

    def addTag(self, newTagID):
        newTagName = self.tagModel.getTagNameFromID(newTagID)
        row = self.ui.assignedTagsList.rowCount()
        self.ui.assignedTagsList.insertRow(row)
        self.ui.assignedTagsList.setItem(row, 0, QtGui.QTableWidgetItem(str(newTagID)))
        self.ui.assignedTagsList.setItem(row, 1, QtGui.QTableWidgetItem(newTagName))

    def addTagFromSpinbox(self):
        newTagID = self.ui.newTagSpinBox.value()
        self.addTag(newTagID)

    def removeTag(self):
        linesToRemove = {}
        for selectedItem in self.ui.assignedTagsList.selectedItems():
            linesToRemove[selectedItem.row()] = True
        for row in sorted(linesToRemove.keys(), reverse=True):
            self.ui.assignedTagsList.removeRow(row)

    def addNewKnowledge(self):
        if self.ui.tagNameEdit.text() == "":
            return
        title = self.ui.tagNameEdit.text()
        description = self.ui.plainTextEdit.toPlainText()
        newKnowledgeID = self.knowledgeModel.addNewKnowledge(title, description)
        for i in range(self.ui.assignedTagsList.rowCount()):
            tagID = int(self.ui.assignedTagsList.item(i,0).data(0))
            self.knowledgeModel.addTagForKnowledge(newKnowledgeID, tagID)
        self.close()

    def updateParentTagName(self, value):
        logging.debug("parentID=%d" % value)
        self.ui.parentTagLabel.setText(self.tagModel.getTagNameFromID(value))
