import logging

from PySide import QtSql
from PySide import QtGui
from PySide import QtCore
from PySide.QtCore import QModelIndex

def getFilterFromIDs(filterIDs, field):
    if filterIDs is None or len(filterIDs) == 0:
        return ""
    filterIDs = list(filterIDs)
    if len(filterIDs) == 1:
        return field+"=%d" % filterIDs[0]
    else:
        filter = field+"=%d" % filterIDs[0]
        for ID in filterIDs[1:]:
            logging.debug(field+"=%d" % ID)
            filter = filter + " OR "+field+"=%d" % ID
        return filter

class TagParentsModel(QtSql.QSqlTableModel):
    def __init__(self, db):
        super(TagParentsModel, self).__init__(None, db)
        self.setTable("tag_parents")
        self.select()
        logging.debug("%d rows in TagParentsModel" % self.rowCount())

    def addParentTag(self, tagID, parentTagID):
        record = QtSql.QSqlRecord()
        record.append(QtSql.QSqlField("ID"))
        record.append(QtSql.QSqlField("tagID"))
        record.append(QtSql.QSqlField("parentTagID"))
        record.setValue(1, tagID)
        record.setValue(2, parentTagID)
        return self.insertRecord(self.rowCount()-1, record)

    def getParentsTags(self, tagID):
        parentTags = []
        self.setFilter("tagID=%d" % tagID)
        self.select()
        logging.debug("%d parents found for tagID=%d" % (self.rowCount(), tagID))
        parentTags = [self.record(i).value("parentTagID") for i in range(self.rowCount())]
        return parentTags


class TagModel(QtSql.QSqlTableModel):
    def __init__(self, db):
        super(TagModel, self).__init__(None, db)
        self.setTable("tags")
        self.select()
        logging.debug("%d rows in TagModel" % self.rowCount())

        self.tagParentsModel = TagParentsModel(db)

    def addTag(self, name):
        self.setFilter("")
        self.setSort(0, QtCore.Qt.SortOrder.DescendingOrder)
        self.select()

        self.setSort(0, QtCore.Qt.SortOrder.AscendingOrder)

    def addTag(self, name):
        self.setFilter("")
        self.setSort(0, QtCore.Qt.SortOrder.AscendingOrder)
        self.select()

        record = QtSql.QSqlRecord()
        record.append(QtSql.QSqlField("ID"))
        record.append(QtSql.QSqlField("name"))
        record.setValue(1, name)
        if not self.insertRecord(self.rowCount()-1, record):
            raise "Tag could not be inserted."
        newID = int(self.record(self.rowCount()-1).value(0))
        logging.debug("newID=%d" % newID)

        return newID

    def removeTag(self, ID):
        self.setFilter("ID=%d" % ID)
        self.select()
        logging.debug("removeTag: self.rowCount()=%d" % self.rowCount())
        if self.rowCount() == 1:
            self.removeRow(0)

    def getTagNameFromID(self, ID):
        self.setFilter("ID=%d" % ID)
        self.select()
        if self.rowCount() == 1:
            return self.record(0).value("name")

    def hasID(self, ID):
        self.setFilter("ID=%d" % ID)
        self.select()
        return self.rowCount() == 1

    def getChildIDs(self, ID, filterIDs=None):
        if filterIDs is not None:
            self.tagParentsModel.setFilter("(parentTagID = %d) AND (%s)" % (ID, getFilterFromIDs(filterIDs, "tagID")))
        else:
            self.tagParentsModel.setFilter("parentTagID = %d" % ID)
        self.tagParentsModel.select()
        childIDs = [self.tagParentsModel.record(i).value("tagID") for i in range(self.tagParentsModel.rowCount())]
        return childIDs

    def getAllChildIDs(self, ID):
        childIDs = self.getChildIDs(ID)
        allChildIDs = childIDs
        for childID in childIDs:
            allChildIDs.extend(self.getAllChildIDs(childID))
        return allChildIDs

    def fillTreeWidgetWithTags(self, treeWidget, checkable=False, IDstoCheck=set(), filterIDs=None):
        treeWidget.clear()

        self.setFilter(getFilterFromIDs(filterIDs, field="ID"))

        logging.debug("tags.filter()=%s" % self.filter())
        self.select()

        logging.debug("tags.rowCount()=%d" % self.rowCount())

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

        self.setFilter(getFilterFromIDs(filterIDs, field="ID"))
        self.select()

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
        self.setFilter(getFilterFromIDs(filterIDs, field="ID"))
        self.select()
        self.tagParentsModel.setFilter(getFilterFromIDs(filterIDs, field="tagID"))
        self.tagParentsModel.select()
        rootTags = {}
        for i in range(self.rowCount()):
            ID = self.record(i).value("ID")
            tag = self.record(i).value("name")
            if not self.hasChildTags(ID):
                rootTags[ID] = tag
        return rootTags

    def getChildTags(self, ID, filterIDs=None):
        self.setFilter(getFilterFromIDs(filterIDs, field="ID"))
        self.select()

        childIDs = self.getChildIDs(ID, filterIDs)
        childTags = {childTagID: self.getTagNameFromID(childTagID) for childTagID in childIDs}
        return childTags

    def hasChildTags(self, ID):
        self.tagParentsModel.setFilter("tagID = %d" % ID)
        self.tagParentsModel.select()
        return self.tagParentsModel.rowCount() > 0

    def getIDsFilteredByName(self, name):
        self.setFilter('name LIKE "%' + name + '%"')
        self.select()
        logging.debug("Found %d tags with name %s" % (self.rowCount(), name))
        IDs = [self.record(i).value("ID") for i in range(self.rowCount())]
        return IDs

    def getParentIDs(self, ID):
        parentIDs = self.tagParentsModel.getParentsTags(ID)
        for parentID in self.tagParentsModel.getParentsTags(ID):
            parentIDs.extend(self.getParentIDs(parentID))
        return parentIDs
