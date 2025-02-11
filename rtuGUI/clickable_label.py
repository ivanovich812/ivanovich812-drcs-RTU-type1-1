from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QLabel


class ClickableLabel(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()

    def mousePressEvent(self, QMouseEvent):
        self.clicked.emit()
