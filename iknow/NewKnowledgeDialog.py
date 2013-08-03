# -*- coding: utf-8 -*-

import logging

from PySide import QtGui
from PySide import QtCore

from ui.Ui_NewKnowledgeDialog import Ui_NewKnowledgeDialog

class NewKnowledgeDialog(QtGui.QDialog):
    def __init__(self, parent, tagModel, tagParentsModel, knowledgeModel, parentID=1):
        super(NewKnowledgeDialog, self).__init__(parent)
        self.ui = Ui_NewKnowledgeDialog()
        self.ui.setupUi(self)

        self.tagModel = tagModel
        self.tagParentsModel = tagParentsModel
        self.knowledgeModel = knowledgeModel

        if parentID is not None:
            self.ui.newTagSpinBox.setValue(parentID)
            self.updateParentTagName(parentID)
            self.addTag()

        self.ui.assignedTagsList.setColumnWidth(0, 35)
        self.ui.assignedTagsList.setColumnWidth(1, 240)

        self.setWindowTitle("Add new piece of knowledge")

        self.ui.newTagSpinBox.valueChanged.connect(self.updateParentTagName)
        self.ui.buttonBox.accepted.connect(self.addNewKnowledge)
        self.ui.buttonBox.rejected.connect(self.close)
        self.ui.addTagButton.clicked.connect(self.addTag)
        self.ui.removeTagButton.clicked.connect(self.removeTag)

    def addTag(self):
        newTagID = self.ui.newTagSpinBox.value()
        newTagName = self.tagModel.getTagNameFromID(newTagID)
        row = self.ui.assignedTagsList.rowCount()
        self.ui.assignedTagsList.insertRow(row)
        self.ui.assignedTagsList.setItem(row, 0, QtGui.QTableWidgetItem(str(newTagID)))
        self.ui.assignedTagsList.setItem(row, 1, QtGui.QTableWidgetItem(newTagName))

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
