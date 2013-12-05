class TreeElement:
    def __init__(self, id, data):
        self.parents = []
        self.childs = []
        self.id = id
        self.data = data

    def isRootElement(self):
        return len(self.parents) == 1 and self.parents[0].id == -1

    def hasChilds(self):
        return len(self.childs) > 0

    def hasParents(self):
        return len(self.parents) > 0 and not self.isRootElement()

    def elementListToIDs(self, elements):
        result = []
        for elem in elements:
            result.append(elem.id)
        return result

    def elementListToDict(self, elements):
        resultDict = {}
        for elem in elements:
            resultDict[elem.id] = elem.data
        return resultDict

    def getChildIDs(self):
        return self.elementListToIDs(self.childs)

    def getChildDict(self):
        return self.elementListToDict(self.childs)

    def getParentIDs(self):
        return self.elementListToIDs(self.parents)

    def getParentDict(self):
        return self.elementListToDict(self.parents)

    def isDeepChildOf(self, parentID):
        for parent in self.parents:
            if parent.id == parentID:
                return True
            elif parent.isDeepChildOf(parentID):
                return True
        return False

    def dumpToString(self, level):
        try:
            dataText = str(self.data)
        except:
            dataText = "???"
        res = "\n" + " "*level + "* %s: %s" % (self.id, dataText)
        for child in self.childs:
            res += child.dumpToString(level + 1)
        return res


class MultiParentTree:
    def __init__(self):
        self._rootElem = TreeElement(-1, "")
        self._elements = {-1: self._rootElem}

    def insertElement(self, id, data):
        # TODO: Throw exceptions here
        if id < 0:
            return False
        if id in self._elements:
            return False

        newElem = TreeElement(id, data)
        self._elements[id] = newElem
        self._rootElem.childs.append(newElem)
        newElem.parents = [self._rootElem]

    def setRelationship(self, parentID, childID):
        if parentID not in self._elements:
            return False
        if childID not in self._elements:
            return False
        if self._elements[parentID].isDeepChildOf(childID):
            return False

        if self._elements[childID].isRootElement():
            self._elements[childID].parents = []
            self._rootElem.childs.remove(self._elements[childID])

        self._elements[childID].parents.append(self._elements[parentID])
        self._elements[parentID].childs.append(self._elements[childID])

    def getRootElements(self):
        return self._rootElem.childs

    def getRootElementsDict(self):
        return self.elementListToDict(self.getRootElements())

    def elementListToDict(self, elements):
        resultDict = {}
        for elem in elements:
            resultDict[elem.id] = elem.data
        return resultDict

    def getElementByID(self, ID):
        if ID in self._elements:
            return self._elements[ID]
        else:
            return None

    def hasID(self, ID):
        return ID in self._elements

    def __str__(self):
        res = "* ROOT"
        for elem in self.getRootElements():
            res += elem.dumpToString(1)
        return res
