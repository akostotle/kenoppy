from enum import Enum

from kenop import KenoP
#from truncater import TruncatR
from PySide6.QtCore import QSysInfo, Signal, Slot, QIODevice, QDir, QFile, QTemporaryFile, QByteArray, QDataStream, QBitArray

class WritR(KenoP):
    write = Signal(int, int, list)
    checkAndSet = Signal(int, QByteArray)
    checkAndSetNext = Signal(int, QByteArray)
    checkAndSetReady = Signal()#(QByteArray)
    aboutToClose = Signal()
    next = Signal()

    class State(Enum):
        UNKNOWN  = 0
        EXISTING = 1
        NEW      = 2

    class HasCombination:
        def __init__(self, exists = False, position = -1):
            self.exists = exists
            self.position = position

    def __init__(self, inputs):
        super().__init__()

        self.directory = QDir("{root:s}/{directory:s}".format(root=self.config.ROOT_DIRECTORY, directory=self.config.RESULTS_DIRECTORY))
        print("WritR::init:", self.directory.absolutePath())

        self.headerSize = 0
        self.header = None

        self.years = list(map(lambda _: _[1], inputs))

        self.write.connect(self.onWrite)
        self.checkAndSet.connect(self.onCheckAndSet)

        self.state = WritR.State.UNKNOWN

        self.isFileOpened = False
        self.isTemporaryFileOpened = False

        #self.findPosition = 0

        print("WriteR:::WriteR:", self.years)

        self.file = QFile(self.fileName())
        if self.file.exists():
            self.file.remove()

        '''
        self.tmpFile = QFile(self.temporaryFileName())
        if self.tmpFile.exists():
            self.tmpFile.remove()
        '''

        '''
        if self.file.open(QIODevice.OpenModeFlag.ReadWrite):
            self.data = QDataStream(self.file)
            self.setHeader()
        else:
            print("WriteR::WriteR: Unable to open file:", self.file.fileName())
        '''
        self.openFile()
        #self.openTemporaryFile()

    def fileName(self):
        return "{root:s}/{directory:s}/R{r:d}.{ext:s}".format(root=self.config.ROOT_DIRECTORY, directory=self.config.RESULTS_DIRECTORY, r=self.config.R, ext=self.config.RESULTS_EXTENSION)

    def openFile(self):
        self.isFileOpened = self.file.open(QIODevice.OpenModeFlag.ReadWrite)

        if self.isFileOpened:
            self.data = QDataStream(self.file)
            self.setHeader()

            #self.openTemporaryFile()
        else:
            print("WriteR::openFile: Unable to open file:", self.fileName())

        return self.isFileOpened

    def temporaryFileName(self):
        return self.fileName() + self.config.TEMPORARY_EXTENSION

    def openTemporaryFile(self):
        if self.tmpFile.exists():
            self.tmpFile.remove()

        if self.tmpFile.open(QIODevice.OpenModeFlag.ReadWrite):
            self.tmpData = QDataStream(self.tmpFile)
        else:
            print("WriteR::openTemporaryFile: Unable to open temporary file:", self.temporaryFileName())

    def setHeader(self):
        self.data.writeRawData(self.config.RESULTS_HEADER)
        self.data.writeUInt8(self.config.R)
        self.data.writeRawData(self.config.RESULTS_HEADER_YEARS_START)

        for year in self.years:
            self.data.writeUInt16(year)

        self.data.writeRawData(self.config.RESULTS_HEADER_YEARS_END)

        self.file.seek(0)
        self.header = self.data.readRawData(self.size())
        self.headerSize = len(self.header)

        print("WritR:::setHeader:", self.headerSize)

    def find(self, values):
        combination = QByteArray()
        for v in values:
            combination.append(v)
            
        print("WritR::find:", combination)

        self.onCheckAndSet(self.headerSize, combination)

    def seek(self, position):
        self.data.device().seek(position)

    def size(self):
        return self.data.device().size()

    def close(self):
        print("WritR::close")
        self.file.close()

    def isCombinationExists(self, combination):
        position = self.headerSize
        
        self.file.seek(position)

        while position < self.size():
            if self.data.readRawData(self.config.R) == combination:
                return self.HasCombination(True, position)

            position += self.file.pos() + self.config.NUMBER_OF_WEEKS*2

        return self.HasCombination(False, position)

    @Slot(int, int, list)
    def onWrite(self, year, week, combination):
        self.year = year
        self.week = week

        print("WritR::onWrite:", combination)

        self.find(combination)

    @Slot(int, list, list)
    def onCheckAndSet(self, position, combination):
        print("WritR::checkAndSet:", position, self.size(), self.headerSize, self.state, combination)
        self.state = WritR.State.UNKNOWN

        #self.seek(position)
        #self.tmpFile.seek(0)
        #print("WritR::onCheckAndSet:", position, self.tmpFile.size())

        # TODO: erőforráshatékonyság!!!
        #self.tmpFile.writeRawData(self.data.readRawData(position))

        hasCombination = self.isCombinationExists(combination)

        print(position, self.size())
        self.file.seek(hasCombination.position)
        if hasCombination.exists:
            #self.file.seek(hasCombination.position)

            values = self.data.readRawData(self.config.R)
            print(values)
            '''
            if values == combination:
                #and self.openTemporaryFile():
                self.state = WritR.State.EXISTING

                self.seek(0)

                position += self.config.R
                # TODO: erőforráshatékonyság!!!
                self.tmpData.writeRawData(self.data.readRawData(position))

                for i in range(self.config.NUMBER_OF_WEEKS):
                    position += self.config.MAX_NUMBER_OF_YEARS_IN_BYTES
                    w = self.config.WEEKS[i]
                    bits = self.readWeek()

                    if w == self.week:
                        bits.setBit(self.config.MAX_NUMBER_OF_YEARS - self.years.index(self.year) - 1)

                    self.tmpData.writeUInt16(self.bitsToBytes(bits))

                # TODO: erőforráshatékonyság!!!
                self.tmpData.writeRawData(self.data.readRawData(self.size() - position))

                #self.checkAndSetReady.emit(combination)

                self.rewriteFileAndDoNext()
            else:
                self.checkAndSetNext.emit(position + self.config.R + self.config.MAX_NUMBER_OF_YEARS_IN_BYTES*self.config.NUMBER_OF_WEEKS, combination)
            '''
        else:
            self.state = WritR.State.NEW

            #length = self.file.size()# - self.headerSize

            print("WritR::onCheckAndSet:", self.state, combination)
            #self.file.seek(0)
            #self.tmpData.writeRawData(self.tmpData.readRawData(length))
            #self.tmpFile.seek(self.file.size())

            self.data.writeRawData(combination)
            #for c in combination:
                #print("WritR::onCheckAndSet::combination:", c)
                #self.data.writeUInt8(c)
                #self.tmpData.writeRawData(c)
                #self.tmpFile.write(c)
                #length += len(c)

            #print(length, combination)

            #self.file.seek(self.size())

            for w in self.config.WEEKS:
                bits = QBitArray(self.config.MAX_NUMBER_OF_YEARS)

                if w == self.week:
                    bits.setBit(self.config.MAX_NUMBER_OF_YEARS - self.years.index(self.year) - 1)

                self.data.writeUInt16(self.bitsToBytes(bits))

                # TODO: hossz bájtokban
                #length += int(16/8)


            #self.file.close()
            self.checkAndSetReady.emit()

            #self.checkAndSetReady.emit(self.file.pos(), combination)
            #self.file.close()
            #print(length)

            #self.tmpFile.commitTransaction()

            #self.rewriteFileAndSetNext(length, combination)

    def rewriteRawData(self, position, data):
        pass

    def rewriteFileAndSetNext(self, length, combination):
        print("WritR::rewriteFileAndSetNext:", length)
        '''
        self.file.close()
        self.file.remove()
        self.tmpFile.close()
        self.tmpFile.rename(self.fileName())
        '''
        #self.file.resize(self.headerSize)
        self.tmpFile.seek(0)
        self.tmpData.writeRawData(self.header)

        #self.file.close()
        #self.tmpFile.close()

        '''
        self.tmpFile.rename(self.fileName())
        self.tmpFile.remove()
        '''

        self.file.close()
        self.tmpFile.close()

        #self.checkAndSetReady.emit(combination)

    def readWeek(self):
        result = QBitArray(self.config.MAX_NUMBER_OF_YEARS)
        value = self.data.readUInt16()
        i = result.size() - 1

        while value > 0 or i >= 0:
            result.setBit(i, value%2)
            value //= 2
            i -= 1

        return result

    def writeWeek(self, bits):
        self.data.writeUInt16(self.bitsToBytes(bits))

    def bytesToBits(self, values):
        result = QBitArray(len(values)*8)
        for i in range(len(values)):
            for b in range(8):
                result.setBit((i*8) + b, values[i] & (1 << (7 - b)))

        return result

    def bitsToBytes(self, bits):
        #TODO: do generic

        values = bits.toUInt32(QSysInfo.Endian.BigEndian)
        values >> 24
        values >> 16

        return values
