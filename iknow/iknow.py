#!/usr/bin/python

import sys
import logging

from PySide import QtGui

from MainWindow import MainWindow
#from NewTagDialog import NewTagDialog

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    #Start Qt-Program
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()

    window.showMaximized()
    sys.exit(app.exec_())
