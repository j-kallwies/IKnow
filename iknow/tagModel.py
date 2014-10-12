import logging
import shutil
from hashlib import sha1
import json
import time
import os

from PySide import QtGui
from PySide import QtCore

from multiParentTree import MultiParentTree


def getFilterFromIDs(filterIDs, field):
    if filterIDs is None or len(filterIDs) == 0:
        return ""
    filterIDs = list(filterIDs)
    if len(filterIDs) == 1:
        return field + "=%d" % filterIDs[0]
    else:
        filter = field + "=%d" % filterIDs[0]
        for ID in filterIDs[1:]:
            logging.debug(field + "=%d" % ID)
            filter = filter + " OR " + field + "=%d" % ID
        return filter

class TagParentsModel():
    def __init__(self, db):
        self.db = db

    def addParentTag(self, tagID, parentTagID):
        pass
        """
        record = QtSql.QSqlRecord()
        record.append(QtSql.QSqlField("ID"))
        record.append(QtSql.QSqlField("tagID"))
        record.append(QtSql.QSqlField("parentTagID"))
        record.setValue(1, tagID)
        record.setValue(2, parentTagID)
        return self.insertRecord(self.rowCount() - 1, record)
        """

class TagModel(QtCore.QAbstractTableModel):
    def __init__(self, db):
        super(TagModel, self).__init__()

        self.db = db

        self.tagParentsModel = TagParentsModel(db)

        logging.debug("%d rows in TagModel" % self.rowCount())

        self.tree = MultiParentTree()
        self.updateTree()

    def rowCount(self):
        #TODO: Implement
        return 0

    def addTag(self, name, parents):
        newData = {"name": name, "parents": parents}

        ID = sha1(name.encode('utf-8') + str(time.time())).hexdigest()

        current_tag_folder = self.db.tagsPath() + ID

        os.makedirs(current_tag_folder)

        tagfile = open(current_tag_folder + '/tag', 'w')
        tagfile.write(json.dumps(newData) + "\n")

        self.db.updateTags()

        return ID

    def removeTag(self, ID):
        print("removeTag(%s)" % ID)
        shutil.rmtree(self.db.tagsPath() + ID)

        self.db.updateTags()

    def getTagNameFromID(self, ID):
        elem = self.tree.getElementByID(ID)
        if elem is not None:
            return elem.data

    def getAllIDs(self):
        return self.db.allTags()

    def hasID(self, ID):
        return self.tree.hasID(ID)

    def getChildIDs(self, ID, filterIDs=None):
        #TODO: Implement filter
        logging.debug("getChildIDs(%s)" % ID)
        if not self.tree.hasID(ID):
            logging.debug("getChildIDs: Tree does not have ID %s" % ID)
            return []
        childIDs = self.tree.getElementByID(ID).getChildIDs()
        logging.debug("getChildIDs: Found child IDs: %s" % childIDs)
        return childIDs

    def getAllChildIDs(self, ID):
        childIDs = self.getChildIDs(ID)
        allChildIDs = childIDs
        for childID in childIDs:
            allChildIDs.extend(self.getAllChildIDs(childID))
        return allChildIDs

    def fillTreeWidgetWithTags(self, treeWidget, checkable=False, IDstoCheck=set(), filterIDs=None):
        self.updateTree(filterIDs)

        # Insert root tags
        rootTags = self.getRootTags(filterIDs)
        logging.debug("rootTags=%s" % str(rootTags))
        for rootID in sorted(rootTags.keys(), reverse=True):
            newElem = QtGui.QTreeWidgetItem([rootTags[rootID], str(rootID)])
            if checkable:
                newElem.setFlags(newElem.flags() | QtCore.Qt.ItemIsUserCheckable)
                newElem.setCheckState(0, QtCore.Qt.Checked)
                if rootID not in IDstoCheck:
                    newElem.setCheckState(0, QtCore.Qt.Unchecked)
                else:
                    self.expandDownToRoot(newElem)
            treeWidget.insertTopLevelItem(0, newElem)
            self.insertChildTags(rootID, newElem, checkable, IDstoCheck, filterIDs)

    def insertChildTags(self, ID, treeWidgetItem, checkable, IDstoCheck, filterIDs):
        if not self.hasID(ID):
            return

        childTags = self.getChildTags(ID, filterIDs)
        logging.debug(self.getTagNameFromID(ID) + ": " + str(childTags))
        for childID in childTags.keys():
            if self.hasID(childID):
                newElem = QtGui.QTreeWidgetItem(treeWidgetItem, [self.getTagNameFromID(childID), str(childID)])
                if checkable:
                    newElem.setFlags(newElem.flags() | QtCore.Qt.ItemIsUserCheckable)
                    newElem.setCheckState(0, QtCore.Qt.Checked)
                    if childID not in IDstoCheck:
                        newElem.setCheckState(0, QtCore.Qt.Unchecked)
                    else:
                        self.expandDownToRoot(newElem)
                if self.hasChildTags(childID):
                    self.insertChildTags(childID, newElem, checkable, IDstoCheck, filterIDs)

    def expandDownToRoot(self, treeWidgetItem):
        treeWidgetItem.setExpanded(True)
        if treeWidgetItem.parent() is not None:
            self.expandDownToRoot(treeWidgetItem.parent())

    def getRootTags(self, filterIDs):
        #TODO: Implement filter
        return self.tree.getRootElementsDict()

    def getChildTags(self, ID, filterIDs=None):
        #TODO: Implement filter
        return self.tree.getElementByID(ID).getChildDict()

    def hasChildTags(self, ID):
        return self.tree.getElementByID(ID).hasParents()

    def getIDsFilteredByName(self, name):
        IDs = []
        for ID in self.db.allTags():
            curr = json.loads(open(self.db.tagsPath() + ID + '/tag').read())
            if name.lower() in curr["name"].lower():
                IDs.append(ID)
        return IDs

    def getParentIDs(self, ID):
        if self.tree.getElementByID(ID) is not None:
            return self.tree.getElementByID(ID).getParentIDs()
        else:
            return []

    def getParentIDsDownToRoot(self, ID):
        allParentIDs = []
        if self.tree.getElementByID(ID) is not None:
            allParentIDs = self.tree.getElementByID(ID).getParentIDs()
            for parentID in allParentIDs:
                allParentIDs.extend(self.getParentIDsDownToRoot(parentID))
        return allParentIDs

    def getParentsTags(self, tagID):
        self.tree.getElementByID(tagID).getParentIDs()

    def updateTree(self, filterIDs=None):
        self.tree = MultiParentTree()

        ID_to_parents = {}

        for ID in self.db.allTags():
            tag_data = json.loads(open(self.db.tagsPath() + ID + '/tag').read())
            tag = tag_data['name']

            # Save parents
            ID_to_parents[ID] = tag_data['parents']

            #logging.debug("ID=%s" % str(ID))
            #logging.debug("tag=%s" % tag)

            if filterIDs is not None:
                if ID not in filterIDs:
                    continue

            self.tree.insertElement(ID, tag)

        for childID, parentIDs in ID_to_parents.iteritems():
            for parentID in parentIDs:
                self.tree.setRelationship(parentID, childID)

        #logging.debug("************ DUMP TREE ************")
        #logging.debug("\n" + str(self.tree))
        #logging.debug("***********************************")
