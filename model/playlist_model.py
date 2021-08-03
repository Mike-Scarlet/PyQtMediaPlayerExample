
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
import typing
import enum

class PlaylistColumnEnum(enum.Enum):
  Title=0
  Count=1

class PlaylistModel(QtCore.QAbstractItemModel):
  def __init__(self, parent: typing.Optional[QtCore.QObject]) -> None:
    super().__init__(parent=parent)
    self.media_playlist = None
    self.data_dict = {}

  def rowCount(self, parent: QtCore.QModelIndex) -> int:
    if self.media_playlist is not None and not parent.isValid():
      return self.media_playlist.mediaCount()
    else:
      return 0

  def columnCount(self, parent: QtCore.QModelIndex) -> int:
    if not parent.isValid():
      return PlaylistColumnEnum.Count.value
    else:
      return 0

  def index(self, row: int, column: int, parent: QtCore.QModelIndex=QtCore.QModelIndex()) -> QtCore.QModelIndex:
    if self.media_playlist is not None and \
       not parent.isValid() and \
       row >= 0 and row < self.media_playlist.mediaCount() and \
       column >= 0 and column < PlaylistColumnEnum.Count.value:
      return self.createIndex(row, column)
    else:
      return QtCore.QModelIndex()

  def parent(self, child: QtCore.QModelIndex):
    return QtCore.QModelIndex()

  def data(self, index: QtCore.QModelIndex, role: int) -> typing.Any:
    if index.isValid() and role == QtCore.Qt.DisplayRole:
      value = self.data_dict.get(index, None)
      if value is None and index.column() == PlaylistColumnEnum.Title.value:
        location = self.media_playlist.media(index.row()).canonicalUrl()
        return QtCore.QFileInfo(location.path()).fileName()
      return value
    return QtCore.QVariant()

  def playlist(self):
    return self.media_playlist

  def setPlaylist(self, playlist: QtMultimedia.QMediaPlaylist):
    if self.media_playlist is not None:
      self.media_playlist.mediaAboutToBeInserted.disconnect(self.beginInsertItems)
      self.media_playlist.mediaInserted.disconnect(self.endInsertItems)
      self.media_playlist.mediaAboutToBeRemoved.disconnect(self.beginRemoveItems)
      self.media_playlist.mediaRemoved.disconnect(self.endRemoveItems)
      self.media_playlist.mediaChanged.disconnect(self.changeItems)

    self.beginResetModel()
    self.media_playlist = playlist

    if self.media_playlist is not None:
      self.media_playlist.mediaAboutToBeInserted.connect(self.beginInsertItems)
      self.media_playlist.mediaInserted.connect(self.endInsertItems)
      self.media_playlist.mediaAboutToBeRemoved.connect(self.beginRemoveItems)
      self.media_playlist.mediaRemoved.connect(self.endRemoveItems)
      self.media_playlist.mediaChanged.connect(self.changeItems)

    self.endResetModel()

  def setData(self, index: QtCore.QModelIndex, value: typing.Any, role: int=QtCore.Qt.EditRole) -> bool:
    self.data_dict[index] = value
    self.dataChanged.emit(index, index)
    return True

  def beginInsertItems(self, start: int, end: int):
    self.data_dict.clear()
    self.beginInsertRows(QtCore.QModelIndex(), start, end)

  def endInsertItems(self):
    self.endInsertRows()

  def beginRemoveItems(self, start: int, end: int):
    self.data_dict.clear()
    self.beginRemoveRows(QtCore.QModelIndex(), start, end)

  def endRemoveItems(self):
    self.endRemoveRows()

  def changeItems(self, start: int, end: int):
    self.data_dict.clear()
    self.dataChanged.emit(self.index(start, 0), 
                          self.index(end, PlaylistColumnEnum.Count.value))  