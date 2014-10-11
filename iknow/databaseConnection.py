# -*- coding: utf-8 -*-

import os
import logging

class DatabaseConnection:
    def __init__(self, path=os.getenv("HOME")+"/.iknow/DB"):
        self._tagsFolderName = 'tags'
        self._knowledgeFolderName = 'knowledge'

        self._baseDBPath = path
        if self._baseDBPath[-1] != '/':
            self._baseDBPath += '/'

        self._databaseSubFolders = [self._tagsFolderName, 'knowledge']

        if not os.path.exists(path):
            os.makedirs(path)

        for subFolder in self._databaseSubFolders:
            fullSubFolderPath = path + '/' + subFolder
            if not os.path.exists(fullSubFolderPath):
                os.makedirs(fullSubFolderPath)

    def tagsPath(self):
        return self._baseDBPath + self._tagsFolderName + '/'

    def knowledgePath(self):
        return self._baseDBPath + self._knowledgeFolderName + '/'

    def listAll(self, subFolder):
        folder = self._baseDBPath + subFolder
        return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]

    def listAllTags(self):
        return self.listAll(self._tagsFolderName)

    def listAllKnowledge(self):
        return self.listAll(self._knowledgeFolderName)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    dbConnection = DatabaseConnection()