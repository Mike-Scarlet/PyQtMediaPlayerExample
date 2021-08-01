
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
import typing

class PlayerControls(QtWidgets.QWidget):
  def __init__(self, parent: QtWidgets.QWidget) -> None:
    super().__init__(parent=parent)
    self.player_state = QtMultimedia.QMediaPlayer.StoppedState
    self.player_muted = False
    self.play_button = None
    self.stop_button = None
    self.next_button = None
    self.previous_button = None
    self.mute_button = None
    self.volume_slider = None
    self.rate_box = None

    self.setupUi()

  def setupUi(self):
    self.play_button = QtWidgets.QToolButton