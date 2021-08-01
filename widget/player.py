
from widget.video_widget import VideoWidget
from model.playlist_model import PlaylistModel
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
import typing

class Player(QtWidgets.QWidget):
  def __init__(self, parent: QtWidgets.QWidget) -> None:
    super().__init__(parent=parent)

    self.video_widget = None
    self.cover_label = None
    self.slider = None

    self.setupUi()

  def setupUi(self):
    self.player = QtMultimedia.QMediaPlayer(self)
    self.play_list = QtMultimedia.QMediaPlaylist()
    self.player.setPlaylist(self.play_list)

    self.player.durationChanged.connect(self.durationChanged)
    self.player.positionChanged.connect(self.positionChanged)
    self.player.metaDataChanged.connect(self.metaDataChanged)
    self.play_list.currentIndexChanged.connect(self.playlistPositionChanged)
    self.player.mediaStatusChanged.connect(self.statusChanged)
    self.player.bufferStatusChanged.connect(self.bufferingProgress)
    self.player.videoAvailableChanged.connect(self.videoAvailableChanged)
    self.player.error.connect(self.displayErrorMessage)
    self.player.stateChanged.connect(self.stateChanged)

    self.video_widget = VideoWidget(self)
    self.player.setVideoOutput(self.video_widget)

    self.play_list_model = PlaylistModel(self)
    self.play_list_model.setPlaylist(self.play_list)

    self.play_list_view = QtWidgets.QListView(self)
    self.play_list_view.setModel(self.play_list_model)
    self.play_list_view.setCurrentIndex(self.play_list_model.index(self.play_list.currentIndex(), 0))

    self.play_list_view.activated.connect(self.jump)

    