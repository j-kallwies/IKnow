# -*- coding: utf-8 -*-

import os
import sys
from PySide import QtGui

from ui.Ui_MainWindow import Ui_MainWindow

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("IKnow")
