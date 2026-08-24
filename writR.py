from enum import Enum

from kenop import KenoP
#from truncater import TruncatR
from PySide6.QtCore import QSysInfo, Signal, Slot, QIODevice, QDir, QFile, QTemporaryFile, QByteArray, QDataStream, QTextStream, QBitArray

class WritR(KenoP):
    write = Signal(int, int, int, list)
    checkAndSet = Signal(int, QByteArray)
    checkAndSetNext = Signal()
    checkAndSetReady = Signal()
    aboutToClose = Signal()
    next = Signal()
    helperNext = Signal()
    saveCurrentWeek = Signal()

    class WeeklyCombination:
        def __init__(self, values, count = 0):
            self.combination = values
            self.hits = []
            #np.ones(self.config.MAX_NUMBER_OF_YEARS, False) #QBitArray(self.config.MAX_NUMBER_OF_YEARS)
            for _ in range(self.config.MAX_NUMBER_OF_YEARS):
                self.hits.appennd(False)

            print(self.hits)

        def __eq__(self, other):
            return self.combination == other.combination

        def __str__(self):
            return "(): "

    class WeeklyCombinations:
        def __init__(self):
            self.combinations = []

        def clear(self):
            self.combinations.clear()

        def append(self, value):
            combination = self.contains(value)
            if combination is not None:
                combination.count += 1
            else:
                value.count = 1
                self.combinations.append(value)

            print("WriR::Combinations::append:", self.combinations)

        def contains(self, value):
            for combination in self.combinations:
                if combination == value:
                    return combination

            return None

    def __init__(self, inputs):
        super().__init__()

        self.root = QDir("{root:s}/{directory:s}".format(root=self.config.ROOT_DIRECTORY, directory=self.config.RESULTS_DIRECTORY))
        print("WritR::init:", self.root.absolutePath())

        self.headerSize = 0
        self.header = None

        self.years = list(map(lambda _: _[1], inputs))

        self.currentWeek = -1

        self.weeklycombinations = self.WeeklyCombinations()

        self.write.connect(self.onWrite)
        self.checkAndSet.connect(self.onCheckAndSet)

        self.isFileOpened = False
        self.isTemporaryFileOpened = False
        print("WriteR:::WriteR:", self.years)

        self.directory = QDir(self.directoryName())
        if self.directory.exists():
            self.directory.removeRecursively()

        self.directory.mkdir(self.directoryName())

        '''
        self.file = QFile(self.fileName())
        if self.file.exists():
            self.file.remove()

        #self.openFile()
        '''

    def directoryName(self):
        return "{root:s}/{directory:s}/R{r:d}".format(root=self.config.ROOT_DIRECTORY, directory=self.config.RESULTS_DIRECTORY, r=self.config.R)

    def fileName(self):
        return "{root:s}/{directory:s}/R{r:d}.{ext:s}".format(root=self.config.ROOT_DIRECTORY, directory=self.config.RESULTS_DIRECTORY, r=self.config.R, ext=self.config.RESULTS_EXTENSION)

    def openFile(self, withHeader = True):
        self.isFileOpened = self.file.open(QIODevice.OpenModeFlag.ReadWrite)

        if self.isFileOpened:
            self.data = QDataStream(self.file)
            if withHeader:
                self.setHeader()
        else:
            print("WriteR::openFile: Unable to open file:", self.fileName())

        return self.isFileOpened

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

        self.startOfHasCombination = self.headerSize

    def find(self, values):
        combination = QByteArray()
        for v in values:
            combination.append(v)

        self.onCheckAndSet(self.headerSize, combination)

    def seek(self, position):
        self.data.device().seek(position)

    def size(self):
        return self.data.device().size()

    def close(self):
        self.file.close()

    def getPositionOfCombination(self, combination):
        self.file.seek(self.headerSize)
        while self.file.pos() < self.file.size():
            data = self.data.readRawData(self.config.R)
            if data == combination:
                return self.file.pos() - self.config.R

            self.file.seek(self.file.pos() + self.config.NUMBER_OF_WEEKS*2)

        return 0

    def contains(self, combiation):
        pass

    @Slot(int, int, int, list)
    def onWrite(self, year, week, day, combination):
        self.year = year
        self.week = week
        self.day = day

        #print("WritR:onWrite:", self.year, self.week, combination)
        #print("WritR:onWrite:", self.combinations.append(self.Combination(combination)))
        #self.combinations.append(self.Combination(combination))

        #self.find(combination)

    @Slot(int, list)
    def onCheckAndSet(self, position, combination):
        #print(self.weeklyCombinations)
        if combination in self.weeklyCombinations:
            #print(list(map(lambda _ : int.from_bytes(_, byteorder="big"), list(combination))))
            pass
        else:
            self.weeklyCombinations.append(combination)

        self.checkAndSetNext.emit()

        #dir = self.directory.path() + ("".join(["/" +  str(_) for _ in list(map(lambda _ : int.from_bytes(_, byteorder="big"), list(combination)))]))

        #print(combination)
        '''
        position = self.getPositionOfCombination(combination)

        if position:
            position += self.config.R
            self.file.seek(position)
                #print(combination, list(map(lambda _ : int.from_bytes(_, byteorder="big"), list(combination))), position)

            position += (self.week - self.config.START_OF_WEEKS)*self.config.MAX_NUMBER_OF_YEARS_IN_BYTES

            self.file.seek(position)
            bits = self.bytesToBits(self.data.readRawData(self.config.MAX_NUMBER_OF_YEARS_IN_BYTES))
            for w in self.config.WEEKS:
                if w == self.week:
                    bits.setBit(self.config.MAX_NUMBER_OF_YEARS - self.years.index(self.year) - 1)

                #print(bits, self.years, position, self.file.pos())
            self.file.seek(position)
            self.data.writeUInt16(self.bitsToBytes(bits))
        else:
            self.file.seek(self.data.device().size())
            self.data.writeRawData(combination)

            for w in self.config.WEEKS:
                bits = QBitArray(self.config.MAX_NUMBER_OF_YEARS)
                if w == self.week:
                    bits.setBit(self.config.MAX_NUMBER_OF_YEARS - self.years.index(self.year) - 1)

                self.data.writeUInt16(self.bitsToBytes(bits))

        if self.currentWeek != self.week and self.day == 1:
            print("WritR::onCheckAndSet:", self.week, self.day)
            #self.file.close()
            self.saveCurrentWeek.emit()
        else:
            self.checkAndSetNext.emit()
        '''

    def setWeek(self, bits):
        bits.setBit(self.config.MAX_NUMBER_OF_YEARS - self.years.index(self.year) - 1)

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
        result = bits.toUInt32(QSysInfo.Endian.BigEndian)

        #TODO: do generic
        result >> 24
        result >> 16

        return result
