from PyQt5.QtCore import Qt, QRect, QSize, QPoint, QEasingCurve, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtWidgets import QCheckBox


class MyCheckBox(QCheckBox):

    def __init__(self,
                 width_size=60,
                 bg_color='#41416b',
                 circle_color='#191929',
                 active_color='#40ff66',
                 animation_curve=QEasingCurve.OutBounce):
        QCheckBox.__init__(self)

        self.setFixedSize(QSize(80, 36))
        self.setCursor(Qt.PointingHandCursor)

        self.bg_color = bg_color
        self._circle_color = circle_color
        self._active_color = active_color

        self._circle_position = 3
        self.animation = QPropertyAnimation(self, b'circle_position', self)
        self.animation.setEasingCurve(animation_curve)
        self.animation.setDuration(500)

        self.stateChanged.connect(self.start_transition)

    @pyqtProperty(float)
    def circle_position(self):
        return self._circle_position

    @circle_position.setter
    def circle_position(self, pos):
        self._circle_position = pos
        self.update()

    def start_transition(self, value):
        self.animation.stop()
        if value:
            self.animation.setEndValue(self.width() - 33)
        else:
            self.animation.setEndValue(4)

        self.animation.start()

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        s = QPen(Qt.transparent)
        p.setPen(s)
        font = QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPixelSize(15)
        font.setBold(True)
        p.setFont(font)

        rect = QRect(0, 0, self.width(), self.height())

        if not self.isChecked():
            p.setBrush(QColor(self.bg_color))
            p.drawRoundedRect(0, 0, rect.width(), self.height(), self.height() / 2, self.height() / 2)

            p.setBrush(QColor(self._circle_color))
            p.drawEllipse(int(self._circle_position), 3, 30, 30)

            p.setPen(QColor(self._circle_color))
            p.drawText(QPoint(int(self.width() / 2), int(self.height() / 1.5)), self.tr("ON"))


        else:
            p.setBrush(QColor(self._active_color))
            p.drawRoundedRect(0, 0, rect.width(), self.height(), self.height() / 2, self.height() / 2)

            p.setBrush(QColor(self._circle_color))
            p.drawEllipse(int(self._circle_position), 3, 30,30)

            p.setPen(QColor(self._circle_color))
            p.drawText(QPoint(int(rect.width() / 7), int(self.height() / 1.5)), self.tr("OFF"))

        p.end()
