# -*- coding: utf-8 -*-

import logging

from PySide import QtGui
from PySide import QtCore

from ui.Ui_NewTagDialog import Ui_NewTagDialog


class NewTagDialog(QtGui.QDialog):
    def __init__(self, parent, tagModel, tagParentsModel, parentID=""):
        super(NewTagDialog, self).__init__(parent)
        self.ui = Ui_NewTagDialog()
        self.ui.setupUi(self)

        self.tagModel = tagModel
        self.tagParentsModel = tagParentsModel

        for ID in tagModel.getAllIDs():
            self.ui.parentTagComboBox.addItem(ID)
        #self.updateParentTagName(self.ui.parentTagComboBox.currentIndex())
        self.updateParentTagName()

        if parentID is not None:
            for i in range(self.ui.parentTagComboBox.count()):
                self.ui.parentTagComboBox.setCurrentIndex(i)
                if str(self.ui.parentTagComboBox.currentText()) == parentID:
                    break
            self.updateParentTagName()
            self.addTag()

        self.setWindowTitle("Add new Tag")

        self.ui.parentTagComboBox.currentIndexChanged.connect(self.updateParentTagName)
        self.ui.addTagButton.clicked.connect(self.addTag)
        self.ui.removeTagButton.clicked.connect(self.removeTag)

    def addTag(self):
        newTagID = str(self.ui.parentTagComboBox.currentText())
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

        parentTagIDs = []
        for i in range(self.ui.assignedTagsList.rowCount()):
            parentTagIDs.append(str(self.ui.assignedTagsList.item(i, 0).data(0)))

        logging.debug("Add new Tag \"%s\" with parents %s..." % (name, str(parentTagIDs)))

        newID = self.tagModel.addTag(name, parentTagIDs)
        logging.debug(self.ui.parentTagComboBox.currentText())
        logging.debug("Inserted new Tag with ID %s" % str(newID))
        self.close()

    def updateParentTagName(self):
        ID = str(self.ui.parentTagComboBox.currentText())
        tagName = self.tagModel.getTagNameFromID(ID)
        if tagName is not None:
            self.ui.parentTagLabel.setText(tagName)
