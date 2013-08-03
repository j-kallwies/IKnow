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

        self.ui.parentTagSpinBox.setValue(parentID)
        self.updateParentTagName(parentID)

        self.setWindowTitle("Add new Tag")

        self.ui.parentTagSpinBox.valueChanged.connect(self.updateParentTagName)

    def accept(self):
        name = self.ui.tagNameEdit.text()

        if name == "":
            return

        logging.debug("Add new Tag \"%s\"..." % name)
        newID = self.tagModel.addTag(name)
        logging.debug(self.ui.parentTagSpinBox.value())
        self.tagParentsModel.addParentTag(newID, self.ui.parentTagSpinBox.value())
        logging.debug("Inserted new Tag with ID %d" % newID)
        self.close()

    def updateParentTagName(self, value):
        logging.debug("parentID=%d" % value)
        self.ui.parentTagLabel.setText(self.tagModel.getTagNameFromID(value))
