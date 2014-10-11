import logging
import time
import os
import json
import shutil

from PySide import QtCore
from PySide import QtGui
from hashlib import sha1

class KnowledgeModel(QtCore.QAbstractTableModel):
    def __init__(self, db, tagModel):
        super(KnowledgeModel, self).__init__()

        self.db = db

        self.tagModel = tagModel

        self._filterByTagIDs = set()
        self._filterByText = ""

        self.columns = ["_id", "title", "description"]

        self.update()

        # TODO: Load rows before!
        logging.debug("%d rows in KnowledgeModel" % self.rowCount())

    def update(self):
        print("update()")

        self._data = []
        for ID in self.db.allKnowledge():
            info_data = json.loads(open(self.db.knowledgePath() + ID + '/info').read())
            tags = set(info_data['tags'])

            curr = info_data
            curr['_id'] = ID
            curr['description'] = open(self.db.knowledgePath() + ID + '/knowledge').read()
            #print("***DATA***: %s" % str(curr))

            # Filter by tags
            if len(self._filterByTagIDs) > 0 and len(tags & self._filterByTagIDs) == 0:
                continue

            # Filter by text
            # TODO: Always accepts "{" and "}" => Fail
            if self._filterByText.lower() not in str(curr).lower():
                continue

            self._data.append(curr)

        topLeft = self.index(0, 0);
        bottomRight = self.index(self.rowCount() - 1, self.columnCount() - 1)

        self.dataChanged.emit(topLeft, bottomRight) # TODO: Do it only if data really changed
        self.layoutChanged.emit() # TODO: Do it only if row- or column-count changed

    def removeRows(self, rowsToRemove):
        for row in rowsToRemove:
            print("Delete(%s)" % self._data[row])
            ID_to_delete = self._data[row]['_id']
            print("Delete %s" % ID_to_delete)
            shutil.rmtree(self.db.knowledgePath() + ID_to_delete)

        self.db.updateKnowledge()
        self.update()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.columns)

    def getDataDictByID(self, ID):
        for data in self._data:
            if data["_id"] == ID:
                return data

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = self.columns[index.column()]
            return self._data[row][col]
        else:
            return None

    def getIDByRow(self, row):
        return self._data[row]["_id"]

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """ Set the headers to be displayed. """
        if role != QtCore.Qt.DisplayRole:
            return None

        if orientation == QtCore.Qt.Horizontal:
            if section < len(self.columns):
                return self.columns[section]
            else:
                return str(section)

        return None

    def setFilterByTagID(self, tagID):
        pass

    def addNewKnowledge(self, title, description, tags, imagePath=None):
        newData = {"type": "BasicKnowledge", "title": title, "tags": tags}

        # TODO: Implement image-saving for file-DB
        #if imagePath is not None:
        #    newData["image"] = open(imagePath, "rb").read()

        ID = sha1(str(newData) + str(time.time())).hexdigest()

        current_knowledge_folder = self.db.knowledgePath() + ID

        os.makedirs(current_knowledge_folder)

        infofile = open(current_knowledge_folder + '/info', 'w')
        infofile.write(json.dumps(newData) + "\n")
        infofile.close()

        open(current_knowledge_folder + '/knowledge', 'w').write(description)

        self.db.updateKnowledge()

        self.update()

        return ID

    """
    imagePath = None does not touch the image
              = "" removes the image
    """
    def updateKnowledge(self, ID, title, description, newTagIDs, imagePath=None):
        data = self.getDataDictByID(ID)
        assert data is not None, 'The knowledge with the ID "%s" was not found!' % str(ID)
        data["title"] = title
        data["description"] = description
        data["tags"] = newTagIDs

        if imagePath is not None:
            if imagePath == "":
                data["image"] = ""
            else:
                data["image"] = open(imagePath, "rb").read()

        # TODO: Move this to a class
        data_for_json = data.copy()
        data_for_json.pop('_id')
        info_data = json.dumps(data_for_json)

        open(self.db.knowledgePath() + ID + '/info','w').write(info_data)

    def getImage(self, ID):
        tempFilename = 'image'
        data = self.getDataDictByID(ID)
        if "image" not in data:
            return None
        else:
            # TODO: Do not save as a file!
            with open(tempFilename, 'wb') as imageFile:
                imageFile.write(data["image"])

            return QtGui.QPixmap(tempFilename)

    def getTagIDsFromKnowledgeID(self, knowledgeID):
        if "tags" in self.getDataDictByID(knowledgeID):
            return self.getDataDictByID(knowledgeID)["tags"]
        else:
            return []

    def reload(self, currentTag=None, filterText=None):
        if currentTag is not None:
            tagIDs = [currentTag]
            tagIDs.extend(self.tagModel.getAllChildIDs(currentTag))
        else:
            tagIDs = []
        logging.debug("reload(): tagIDs = %s" % str(tagIDs))
        self._filterByTagIDs = set(tagIDs)
        self._filterByText = filterText
        self.update()
