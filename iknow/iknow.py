#!/usr/bin/python

from PySide import QtGui
from MainWindow import MainWindow
import sys

if __name__ == "__main__":
    #Start Qt-Program
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()

    window.show()
    sys.exit(app.exec_())
