import logging
import os
import json

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

        self.columns = ["_id", "_rev", "title", "description"]

        self.update()

        # TODO: Load rows before!
        logging.debug("%d rows in KnowledgeModel" % self.rowCount())

    def update(self):
        print("update()")

        db_folder = "/home/jaka/.iknow/DB/"
        knowledge_folder = db_folder + "knowledge/"

        self._data = []
        for curr in self.db.all('id'):
            if curr["_t"] == "knowledge":
                tags = set(curr["tags"])

                new_id_tags = []
                for tag in tags:
                    print('tag-ID='+str(tag))
                    tag_name = self.tagModel.getTagNameFromID(tag)
                    print(tag_name)
                    if tag_name is not None:
                        new_id_tags.append(sha1(tag.encode('utf-8')).hexdigest())

                #print("***DATA***: %s" % str(curr))

                # Save to new Database-Structure
                new_knowledge_id = sha1(str(curr)).hexdigest()
                print('new_knowledge_id='+new_knowledge_id)

                current_knowledge_folder = knowledge_folder + new_knowledge_id + '/'

                if not os.path.exists(current_knowledge_folder):
                    os.makedirs(current_knowledge_folder)

                infofile = open(current_knowledge_folder+'info', 'w')
                info_data = {'type': 'BasicKnowledge', 'title': curr["title"].encode('utf-8'), 'tags': new_id_tags}
                infofile.write(json.dumps(info_data) + "\n")
                infofile.close()

                knowledgefile = open(current_knowledge_folder+'knowledge', 'w')
                knowledgefile.write(curr["description"].encode('utf-8'))
                knowledgefile.close()

                tempFilename = current_knowledge_folder+'image.png'
                if "image" in curr:
                    # TODO: Do not save as a file!
                    print('FOUND AN IMAGE! => Save it to ' + tempFilename)
                    with open(tempFilename, 'wb') as imageFile:
                        imageFile.write(curr["image"])

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
            self.db.delete(self._data[row])
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
        newData = {"_t": "knowledge", "title": title, "description": description, "tags": tags}

        if imagePath is not None:
            newData["image"] = open(imagePath, "rb").read()

        res = self.db.insert(newData)

        self.update()

        return res['_id']

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

        self.db.update(data)

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
