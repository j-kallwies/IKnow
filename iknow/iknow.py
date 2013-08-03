#!/usr/bin/python

import sys
import logging

from PySide import QtGui

from MainWindow import MainWindow

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    #Start Qt-Program
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()

    window.show()
    sys.exit(app.exec_())
