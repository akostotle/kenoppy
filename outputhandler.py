from PySide6 import QtCore
from PySide6.QtCore import Signal, Slot
from PySide6.QtCore import QByteArray, QFileDevice, QFile, QDataStream


class OutputHandler(QtCore.QObject):

    #ROOT = "/home/akos/kenoppy" #"/Volumes/ExtremeSSD/akos/kenoppy"
    FILE_TYPE = "kpb"
    YEARS_START= 'Y'
    YEARS_STOP = 'S'

    setCombination = Signal()

    def __init__(self, parent):
        super().__init__(parent)

        self.controller = parent
        self.controller.combinationReady.connect(self.onCombinationReady)

        self.isOpened = False

        self.r = parent.r
        self.filename = "R{r:d}.{extension:s}".format(r=self.r, extension=self.FILE_TYPE)

        self.headerSize = 0

        #self.connect.setData(self)
        #self.parent.nextCombination.connect(self)

        self.open()
        self.setHeader([2023])
        #self.close()

    def open(self):
        self.file = QFile(self.filename)
        if self.file.exists():
            self.file.remove()

        if self.file.open(QFileDevice.OpenModeFlag.ReadWrite):
            self.stream = QDataStream(self.file)
        else:
            print("ERROR: Unable to open file to write")

    def setHeader(self, years):
        for _ in (list(map(lambda _ : _, self.FILE_TYPE.upper()))):
            self.stream.writeRawData(_)

        self.stream.writeRawData(QByteArray.number(self.r))

        self.stream.writeRawData(self.YEARS_START)

        self.stream.writeRawData(QByteArray.number(len(years)))

        for _ in (list(map(lambda _ : _, years))):
            self.stream.writeRawData(QByteArray.number(_))

        self.stream.writeRawData(self.YEARS_STOP)

        self.headerSize = self.file.size()

        print("OutputHandler::setHeader:", self.headerSize)

    @Slot()
    def onCombinationReady(self):
        print("OutputHandler::onCombinationReady", len(self.controller.combinations.result))
        #print(self.controller.data[2023][42])
        #print("OutputHandler::onCombinationReady:", self.controller.combinations.result)
        #self.stream.writeRawData("\n")
        for combination in self.controller.combinations.result:
            self.stream.writeRawData("[")
            for c in combination:
                self.stream.writeRawData(QByteArray.number(c))
                #self.stream.writeInt8(c)
                if c is not combination[-1]:
                    self.stream.writeRawData(",")

            self.stream.writeRawData("]")





            #self.stream.writeRawData("\n")



    @Slot(list)
    def setData(self, combination):
        print("OutputHandler::setData:", combination)

        self.parent.nextCombination().emit()

    def close(self):
        if self.file.isOpen():
            self.file.close()
