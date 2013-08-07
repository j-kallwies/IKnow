#!/usr/bin/env python

import context
import logging

from iknow.multiParentTree import MultiParentTree


class TestMultiParentTree:
    def test_insertNegativeID(self):
        testTree = MultiParentTree()
        assert testTree.insertElement(-1, "") is False

    def test_doubleInsertSameID(self):
        testTree = MultiParentTree()
        testTree.insertElement(1, "Foo")
        assert testTree.insertElement(1, "Bar") is False

    def test_insertFirstLevel(self):
        testTree = MultiParentTree()
        testTree.insertElement(1, "Foo")
        testTree.insertElement(2, "Bar")

        rootElements = testTree.getRootElementsDict()
        assert len(rootElements) == 2
        assert rootElements[1] == "Foo"
        assert rootElements[2] == "Bar"

    def test_insertSingleChildElement(self):
        testTree = MultiParentTree()
        testTree.insertElement(1, "Foo")
        testTree.insertElement(2, "Bar")
        testTree.setRelationship(1, 2)  # Bar shall be a child of Foo

        rootElements = testTree.getRootElements()
        assert len(rootElements) == 1
        assert rootElements[0].data == "Foo"
        assert len(rootElements[0].childs) == 1
        assert rootElements[0].childs[0].data == "Bar"
        assert len(rootElements[0].childs[0].parents) == 1
        assert rootElements[0].childs[0].parents[0].data == "Foo"

        assert testTree.hasID(1) is True
        assert testTree.hasID(2) is True
        assert testTree.hasID(3) is False

    def test_insertMultipleChildElement(self):
        testTree = MultiParentTree()
        testTree.insertElement(1, "Foo")
        testTree.insertElement(2, "Bar")
        testTree.insertElement(3, "42")
        testTree.setRelationship(1, 2)  # Bar shall be a child of Foo
        testTree.setRelationship(1, 3)  # 42 shall be a child of Foo

        assert testTree.setRelationship(1, 100) is False  # Test if the childID does not exist
        assert testTree.setRelationship(100, 1) is False  # Test if the parrentID does not exist

        rootElements = testTree.getRootElements()
        assert len(rootElements) == 1
        assert rootElements[0].data == "Foo"
        assert len(rootElements[0].childs) == 2

        assert testTree.getElementByID(1).getChildIDs() == [2, 3]

        assert testTree.getElementByID(100) is None

        assert testTree.getElementByID(1).hasParents() is False
        assert testTree.getElementByID(2).hasParents() is True

        assert rootElements[0].hasChilds() is True
        assert rootElements[0].childs[0].data == "Bar"
        assert rootElements[0].childs[1].data == "42"

        assert rootElements[0].getChildDict() == {2: 'Bar', 3: '42'}

        assert len(rootElements[0].childs[0].parents) == 1
        assert rootElements[0].childs[0].getParentIDs() == [1]
        assert rootElements[0].childs[0].getParentDict() == {1: "Foo"}
        assert rootElements[0].childs[0].hasChilds() is False
        assert rootElements[0].childs[0].parents[0].data == "Foo"
        assert len(rootElements[0].childs[1].parents) == 1
        assert rootElements[0].childs[1].parents[0].data == "Foo"
        assert rootElements[0].childs[1].hasChilds() is False

    def test_ringRelationship(self):
        testTree = MultiParentTree()
        testTree.insertElement(1, "A")
        testTree.insertElement(2, "B1")
        testTree.insertElement(3, "B2")
        testTree.insertElement(4, "C")
        testTree.insertElement(5, "D")

        testTree.setRelationship(1, 2)  # B1 shall be a child of A
        testTree.setRelationship(1, 3)  # B2 shall be a child of A
        testTree.setRelationship(3, 4)  # C shall be a child of B2
        testTree.setRelationship(4, 5)  # D shall be a child of C

        # Check if ringRelationships are avoided
        assert testTree.setRelationship(2, 1) is False  # A can not be a child of B1
        assert testTree.setRelationship(5, 1) is False  # A can not be a child of D
        assert testTree.setRelationship(5, 3) is False  # B2 can not be a child of D
        assert testTree.setRelationship(5, 4) is False  # C can not be a child of D
