from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStyledItemDelegate


class FontDelegate(QStyledItemDelegate):
    def createEditor(self, parent, opt, index):
        editor = super().createEditor(parent, opt, index)
        font = index.data(Qt.FontRole)
        if font is not None:
            editor.setFont(font)
            # editor.setAlignment(Qt.AlignHCenter)
            # editor.setStyleSheet('color: grey')
        return editor