# -*- coding: utf-8 -*-

import logging
import os

from PySide import QtGui

from ui.Ui_NewKnowledgeDialog import Ui_NewKnowledgeDialog

maxWidth = 300
maxHeight = 200

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
            self.knowledgeID = None
        else:
            self.setWindowTitle("Edit a piece of knowledge")
            self.ui.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Apply | QtGui.QDialogButtonBox.Reset)
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Reset).clicked.connect(self.resetDataFromModel)
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.updateModel)
            self.ui.buttonBox.accepted.connect(self.updateModelAndClose)

            self.knowledgeID = self.knowledgeModel.getIDByRow(editRow)
            logging.debug("self.knowledgeID=%s" % self.knowledgeID)
            self.resetDataFromModel()

        self.ui.buttonBox.rejected.connect(self.close)
        self.ui.addImageButton.clicked.connect(self.addImage)
        self.ui.removeImageButton.clicked.connect(self.removeImage)
        self.ui.saveImageButton.clicked.connect(self.saveImage)

        self._imagePath = None

    def addImage(self):
        print("addImage()")
        dialogResult = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open Image"), os.getenv("HOME"), self.tr("Image Files (*.png *.jpg *.bmp)"))
        fileName = str(dialogResult[0])
        print("fileName=%s" % str(fileName))

        #self.knowledgeModel.addImage(self.knowledgeID, fileName)
        self._imagePath = fileName

        self.drawImage(QtGui.QPixmap(fileName))

    def removeImage(self):
        print("removeImage()")
        self.clearImage()
        self._imagePath = ""

    def saveImage(self):
        print("saveImage()")
        dialogResult = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save Image"), os.getenv("HOME"), self.tr("PNG Files (*.png)"))
        fileName = str(dialogResult[0])
        print("fileName=%s" % str(fileName))

        if self.knowledgeID is None:
            image = QtGui.QPixmap(self._imagePath)
        else:
            image = self.knowledgeModel.getImage(self.knowledgeID)

        if image is not None:
            image.save(fileName)

    def clearImage(self):
        self.drawImage(QtGui.QPixmap())

    def getSelectedTagIDs(self):
        logging.debug("topLevelItemCount()=%d" % self.ui.tagTreeWidget.topLevelItemCount())
        tagIDs = []
        for i in range(self.ui.tagTreeWidget.topLevelItemCount()):
            rootItem = self.ui.tagTreeWidget.topLevelItem(i)
            if int(rootItem.checkState(0)):
                tagIDs.append(str(rootItem.data(1, 0)))
            tagIDs.extend(self.getSelectedTagIDsFromChilds(rootItem))
        return tagIDs

    def getSelectedTagIDsFromChilds(self, treeWidgetItem):
        tagIDs = []
        for i in range(treeWidgetItem.childCount()):
            childItem = treeWidgetItem.child(i)
            if int(childItem.checkState(0)):
                tagIDs.append(str(childItem.data(1, 0)))
            tagIDs.extend(self.getSelectedTagIDsFromChilds(childItem))
        return tagIDs

    def drawImage(self, image):
        print("image-size: %d x %d" % (image.width(), image.height()))
        if image.width() > maxWidth:
            image = image.scaledToWidth(maxWidth)
        if image.height() > maxHeight:
            image = image.scaledToWidth(maxWidth)
        self.ui.imageLabel.setPixmap(image)

    def resetDataFromModel(self):
        self.addTagsFromModel()

        data = self.knowledgeModel.getDataDictByID(self.knowledgeID)
        self.ui.tagNameEdit.setText(data["title"])
        self.ui.plainTextEdit.setPlainText(data["description"])

        image = self.knowledgeModel.getImage(self.knowledgeID)
        if image is not None:
            self.drawImage(image)

    def updateModel(self):
        logging.debug("updateModel")
        title = self.ui.tagNameEdit.text()
        description = self.ui.plainTextEdit.toPlainText()
        newTagIDs = self.getSelectedTagIDs()
        self.knowledgeModel.updateKnowledge(self.knowledgeID, title, description, newTagIDs, imagePath=self._imagePath)

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
        tagIDs = self.getSelectedTagIDs()
        logging.debug("getSelectedTagIDs()=%s" % str(tagIDs))
        self.knowledgeModel.addNewKnowledge(title, description, tagIDs)
        self.close()

    def updateParentTagName(self, value):
        logging.debug("parentID=%d" % value)
        self.ui.parentTagLabel.setText(self.tagModel.getTagNameFromID(value))
