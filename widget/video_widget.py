
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimediaWidgets
import typing

class VideoWidget(QtMultimediaWidgets.QVideoWidget):
  def __init__(self, parent: typing.Optional[QtWidgets.QWidget]) -> None:
    super().__init__(parent=parent)
    self.setSizePolicy(QtWidgets.QSizePolicy(
      QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored))
    
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtCore.Qt.black)
    self.setPalette(palette)

    self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)

  def keyPressEvent(self, event: QtGui.QKeyEvent):
    if event.key() == QtCore.Qt.Key_Escape and self.isFullScreen():
      self.setFullScreen(False)
      event.accept()
    elif event.key() == QtCore.Qt.Key_Enter and \
         (event.modifiers() & QtCore.Qt.Key_Alt):
      self.setFullScreen(not self.isFullScreen())
      event.accept()
    else:
      super(QtMultimediaWidgets.QVideoWidget, self).keyPressEvent(event)

  def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
    self.setFullScreen(not self.isFullScreen())
    event.accept()

  def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
      return super().mousePressEvent(a0)