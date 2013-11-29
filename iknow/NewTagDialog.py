# -*- coding: utf-8 -*-

import logging

from PySide import QtGui
from PySide import QtCore

from ui.Ui_NewTagDialog import Ui_NewTagDialog


class NewTagDialog(QtGui.QDialog):
    def __init__(self, parent, tagModel, tagParentsModel, parentID=1):
        super(NewTagDialog, self).__init__(parent)
        self.ui = Ui_NewTagDialog()
        self.ui.setupUi(self)

        self.tagModel = tagModel
        self.tagParentsModel = tagParentsModel

        if parentID is not None:
            self.ui.parentTagSpinBox.setValue(parentID)
            self.updateParentTagName(parentID)
            self.addTag()

        self.setWindowTitle("Add new Tag")

        self.ui.parentTagSpinBox.valueChanged.connect(self.updateParentTagName)
        self.ui.addTagButton.clicked.connect(self.addTag)
        self.ui.removeTagButton.clicked.connect(self.removeTag)

    def addTag(self):
        newTagID = self.ui.parentTagSpinBox.value()
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

    def accept(self):
        name = self.ui.tagNameEdit.text()

        if name == "":
            return

        logging.debug("Add new Tag \"%s\"..." % name)
        newID = self.tagModel.addTag(name)
        logging.debug(self.ui.parentTagSpinBox.value())
        for i in range(self.ui.assignedTagsList.rowCount()):
            parentTagID = self.ui.assignedTagsList.item(i, 0).data(0)
            self.tagParentsModel.addParentTag(newID, parentTagID)
        logging.debug("Inserted new Tag with ID %s" % str(newID))
        self.close()

    def updateParentTagName(self, value):
        logging.debug("parentID=%d" % value)
        self.ui.parentTagLabel.setText(self.tagModel.getTagNameFromID(value))
