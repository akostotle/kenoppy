from PySide6 import QtCore


class TruncatR(QtCore.QObject):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

    def __init__(self):
        pass

    def set(self, filename, position):
        self.position = position

        self.open(filename)

    def open(self, filenme):
        pass

    def setBeginning(self):
        pass

    def overwrite(self, position, data):
        pass

    def setEnding(self):
        pass

    def close(self):
        pass
