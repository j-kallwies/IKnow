# -*- coding: utf-8 -*-

import os

#import CodernityDB
from CodernityDB.database import Database
from CodernityDB.hash_index import HashIndex
import logging

from hashlib import md5

class TagIndex(HashIndex):

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = '16s'
        super(TagIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        if data['_t'] == 'tag':
            tagName = data['name']
            # if not isinstance(login, basestring):
            #     login = str(login)
            return md5(tagName).digest(), {'name': data['name'], 'parents': data['parents']}

    def make_key(self, key):
        return md5(key).digest()


class DatabaseConnection:
    def __init__(self, path=os.getenv("HOME")+"/.iknow/DB"):
        if not os.path.exists(path):
            os.makedirs(path)

        self.db = Database(path)

        tagsIndex = TagIndex(self.db.path, 'tags')

        print(tagsIndex)

        if self.db.exists():
            self.db.open()
            self.db.reindex()
        else:
            self.db.create()
            #self.db.add_index(tagsIndex)

        """
        print("********************************")
        print("FULL DB CONTENT:")
        print("********************************")
        for curr in self.db.all('id'):
            print curr
        print("********************************")
        """

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    dbConnection = DatabaseConnection()