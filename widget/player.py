
from widget.player_controls import PlayerControls
from widget.video_widget import VideoWidget
from model.playlist_model import PlaylistModel
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
import typing, os

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

    self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
    self.slider.setRange(0, self.player.duration)

    self.label_duration = QtWidgets.QLabel(self)
    self.slider.sliderMoved.connect(self.seek)

    self.open_button = QtWidgets.QPushButton("Open", self)
    self.open_button.clicked.connect(self.open)

    self.controls = PlayerControls(self)
    self.controls.setState(self.player.state())
    self.controls.setVolume(self.player.volume())
    self.controls.setMuted(self.player.isMuted())

    self.controls.play.connect(self.player.play)
    self.controls.pause.connect(self.player.pause)
    self.controls.stop.connect(self.player.stop)
    self.controls.next.connect(self.play_list.next)
    self.controls.previous.connect(self.previousClicked)
    self.controls.changeVolume.connect(self.player.setVolume)
    self.controls.changeMuting.connect(self.player.setMuted)
    self.controls.changeRate.connect(self.player.setPlaybackRate)

    self.controls.stop.connect(self.video_widget.update)

    self.player.stateChanged.connect(self.controls.setState)
    self.player.volumeChanged.connect(self.controls.setVolume)
    self.player.mutedChanged.connect(self.controls.setMuted)

    self.full_screen_button = QtWidgets.QPushButton("FullScreen", self)
    self.full_screen_button.setCheckable(True)

    self.display_layout = QtWidgets.QHBoxLayout()
    self.display_layout.addWidget(self.video_widget, 2)
    self.display_layout.addWidget(self.play_list_view)

    self.control_layout = QtWidgets.QHBoxLayout()
    self.control_layout.setMargin(0)
    self.control_layout.addWidget(self.open_button)
    self.control_layout.setStretch(1)
    self.control_layout.addWidget(self.controls)
    self.control_layout.addStretch(1)
    self.control_layout.addWidget(self.full_screen_button)

    self.slider_layout = QtWidgets.QHBoxLayout()
    self.slider_layout.addWidget(self.slider)
    self.slider_layout.addWidget(self.label_duration)

    self.main_layout = QtWidgets.QVBoxLayout()
    self.main_layout.addLayout(self.display_layout)
    self.main_layout.addLayout(self.slider_layout)
    self.main_layout.addLayout(self.control_layout)

    self.setLayout(self.main_layout)

    if self.player.isAvailable():
      QtWidgets.QMessageBox.warning(
        self, "Service not available",
        "The QMediaPlayer object does not have a valid service. \n \
         Please check the media service plugins are installed."
      )
      self.controls.setEnabled(False)
      self.play_list_view.setEnabled(False)
      self.open_button.setEnabled(False)
      self.full_screen_button.setEnabled(False)

    self.metaDataChanged()
  
  def open(self):
    file_dialog = QtWidgets.QFileDialog(self)
    file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
    file_dialog.setWindowTitle("Open Files")
    supported_mime_types = self.player.supportedMimeTypes()
    if len(supported_mime_types) == 0:
      supported_mime_types.append("audio/x-m3u")
      file_dialog.setMimeTypeFilters(supported_mime_types)
    file_dialog.setDirectory(QtCore.QStandardPaths.standardLocations(
      QtCore.QStandardPaths.MoviesLocation).value(0, QtCore.QDir.homePath()))

    if file_dialog.exec() == QtWidgets.QDialog.Accepted:
      self.addToPlaylist(file_dialog.selectedUrls())
    
  def isPlaylist(self, url: QtCore.QUrl):
    if not url.isLocalFile():
      return False
    file_info = url.toLocalFile()
    return os.path.exists(file_info) and not file_info.split(".")[-1].lower() == "m3u"
  
  def addToPlaylist(self, urls: typing.List[QtCore.QUrl]):
    for url in urls:
      if self.isPlaylist(url):
        self.play_list.load(url)
      else:
        self.play_list.addMedia(url)
  
  def durationChanged(self, duration: int):
    self.duration = duration / 1000
    self.slider.setMaximum(self.duration / 1000)

  def PositionChanged(self, progress: int):
    if not self.slider.isSliderDown():
      self.slider.setValue(progress / 1000)
    self.updateDurationInfo(progress / 1000)

  def metaDataChanged(self):
    if self.player.isMetaDataAvailable():
      self.setTrackInfo("{} - {}".format(
        self.player.metaData(QtMultimedia.QMediaMetaData.AlbumArtist),
        self.player.metaData(QtMultimedia.QMediaMetaData.Title),
      ))

  def previousClicked(self):
    # Go to previous track if we are within the first 5 seconds of playback
    # Otherwise, seek to the beginning.
    if self.player.position() <= 5000:
      self.play_list.previous()
    else:
      self.player.setPosition(0)

  def jump(self, index: QtCore.QModelIndex):
    if index.isValid():
      self.play_list.setCurrentIndex(index.row())
      self.player.play()

  def playlistPositionChanged(self, current_item: int):
    self.play_list_view.setCurrentIndex(self.play_list_model.index(current_item, 0))

  def seek(self, seconds: int):
    self.player.setPosition(seconds * 1000)

  def statusChanged(self, status: QtMultimedia.QMediaPlayer.MediaStatus):
    self.handleCursor(status)

    if status == QtMultimedia.QMediaPlayer.UnknownMediaStatus or \
       status == QtMultimedia.QMediaPlayer.NoMedia or \
       status == QtMultimedia.QMediaPlayer.LoadedMedia or \
       status == QtMultimedia.QMediaPlayer.BufferingMedia or \
       status == QtMultimedia.QMediaPlayer.BufferedMedia:
      self.setStatusInfo("")
    elif status == QtMultimedia.QMediaPlayer.LoadingMedia:
      self.setStatusInfo("Loading")
    elif status == QtMultimedia.QMediaPlayer.StalledMedia:
      self.setStatusInfo("Media Stalled")
    elif status == QtMultimedia.QMediaPlayer.EndOfMedia:
      QtWidgets.QApplication.alert(self)
    elif status == QtMultimedia.QMediaPlayer.InvalidMedia:
      self.displayErrorMessage()
  
  def stateChanged(self, state: QtMultimedia.QMediaPlayer.State):
    pass # since no histogram

  def handleCursor(self, status: QtMultimedia.QMediaPlayer.MediaStatus):
    if status == QtMultimedia.QMediaPlayer.LoadingMedia or \
       status == QtMultimedia.QMediaPlayer.BufferingMedia or \
       status == QtMultimedia.QMediaPlayer.StalledMedia:
      self.setCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
    else:
      self.unsetCursor()

  def bufferingProgress(self, progress: int):
    self.setStatusInfo("Buffering {}%".format(progress))

  def videoAvailableChanged(self, available: bool):
    if not available:
      self.full_screen_button.clicked.disconnect(self.video_widget.setFullScreen)
      self.video_widget.fullScreenChanged.disconnect(self.full_screen_button.setChecked)
      self.video_widget.setFullScreen(False)
    else:
      self.full_screen_button.clicked.connect(self.video_widget.setFullScreen)
      self.video_widget.fullScreenChanged.connect(self.full_screen_button.setChecked)
      if self.full_screen_button.isChecked():
        self.video_widget.setFullScreen(True)
    
  