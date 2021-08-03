
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
import typing

class PlayerControls(QtWidgets.QWidget):
  play = QtCore.pyqtSignal()
  pause = QtCore.pyqtSignal()
  stop = QtCore.pyqtSignal()
  next = QtCore.pyqtSignal()
  previous = QtCore.pyqtSignal()
  changeVolume = QtCore.pyqtSignal(int)
  changeMuting = QtCore.pyqtSignal(bool)
  changeRate = QtCore.pyqtSignal(float)

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
    self.play_button = QtWidgets.QToolButton(self)
    self.play_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))

    self.play_button.clicked.connect(self.playClicked)

    self.stop_button = QtWidgets.QToolButton(self)
    self.stop_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaStop))
    self.stop_button.setEnabled(False)

    self.stop_button.clicked.connect(self.stop)

    self.next_button = QtWidgets.QToolButton(self)
    self.next_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipForward))

    self.next_button.clicked.connect(self.next)
    
    self.previous_button = QtWidgets.QToolButton(self)
    self.previous_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipBackward))

    self.previous_button.clicked.connect(self.previous)

    self.mute_button = QtWidgets.QToolButton(self)
    self.mute_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaVolume))

    self.mute_button.clicked.connect(self.muteClicked)

    self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
    self.volume_slider.setRange(0, 100)

    self.volume_slider.valueChanged.connect(self.onVolumeSliderValueChanged)

    self.rate_box = QtWidgets.QComboBox(self)
    self.rate_box.addItem("0.5x", 0.5)
    self.rate_box.addItem("1.0x", 1.0)
    self.rate_box.addItem("2.0x", 2.0)
    self.rate_box.setCurrentIndex(1)

    self.rate_box.activated.connect(self.updateRate)

    self.box_layout = QtWidgets.QHBoxLayout()
    self.box_layout.setContentsMargins(0,0,0,0)
    self.box_layout.addWidget(self.stop_button)
    self.box_layout.addWidget(self.previous_button)
    self.box_layout.addWidget(self.play_button)
    self.box_layout.addWidget(self.next_button)
    self.box_layout.addWidget(self.mute_button)
    self.box_layout.addWidget(self.volume_slider)
    self.box_layout.addWidget(self.rate_box)
    self.setLayout(self.box_layout)

  def state(self):
    return self.player_state

  @QtCore.pyqtSlot(QtMultimedia.QMediaPlayer.State)
  def setState(self, state: QtMultimedia.QMediaPlayer.State):
    if state != self.player_state:
      self.player_state = state

      if (state == QtMultimedia.QMediaPlayer.StoppedState):
        self.stop_button.setEnabled(False)
        self.play_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
      elif (state == QtMultimedia.QMediaPlayer.PlayingState):
        self.stop_button.setEnabled(True)
        self.play_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause))
      elif (state == QtMultimedia.QMediaPlayer.PausedState):
        self.stop_button.setEnabled(True)
        self.play_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))

  def volume(self):
    linear_volume = QtMultimedia.QAudio.convertVolume(self.volume_slider.value() / 100,
                                                      QtMultimedia.QAudio.LogarithmicVolumeScale,
                                                      QtMultimedia.QAudio.LinearVolumeScale)

    return round(linear_volume * 100)

  @QtCore.pyqtSlot(int)
  def setVolume(self, volume: int):
    logarithmic_volume = QtMultimedia.QAudio.convertVolume(
      volume / 100,
      QtMultimedia.QAudio.LinearVolumeScale,
      QtMultimedia.QAudio.LogarithmicVolumeScale
    )
    self.volume_slider.setValue(round(logarithmic_volume * 100))

  def isMuted(self):
    return self.player_muted

  @QtCore.pyqtSlot(bool)
  def setMuted(self, muted: bool):
    if muted != self.player_muted:
      self.player_muted = muted
      if self.player_muted == True:
        self.mute_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaVolumeMuted))
      else:
        self.mute_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaVolume))

  def playClicked(self):
    if self.player_state == QtMultimedia.QMediaPlayer.StoppedState or \
       self.player_state == QtMultimedia.QMediaPlayer.PausedState:
      self.play.emit()
    elif self.player_state == QtMultimedia.QMediaPlayer.PlayingState:
      self.pause.emit()

  def muteClicked(self):
    # TODO: why it doesn't change self.player_muted
    self.changeMuting.emit(self.player_muted)

  def playbackRate(self):
    return self.rate_box.itemData(self.rate_box.currentIndex()).toDouble()

  @QtCore.pyqtSlot(float)
  def setPlaybackRate(self, rate: float):
    for i in range(self.rate_box.count()):
      if QtCore.qFuzzyCompare(rate, float(self.rate_box.itemData(i).toDouble())):
        self.rate_box.setCurrentIndex(i)
        return
    
    self.rate_box.addItem("{:.1f}x".format(rate), rate)
    self.rate_box.setCurrentIndex(self.rate_box.count() - 1)

  def updateRate(self):
    self.changeRate.emit(self.playbackRate())
  
  def onVolumeSliderValueChanged(self):
    self.changeVolume.emit(self.volume())