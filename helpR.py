from kenop import KenoP

from PySide6.QtCore import QObject, Signal, Slot, QByteArray, QDir, QIODevice, QFile, QDataStream


class HelpR(KenoP):
    next = Signal()
    currentChanged = Signal(list)
    ready = Signal()

    def __init__(self):
        super().__init__()

        self.data = []
        self.input = []

        self.length = self.nCr(self.config.N, self.config.R)

        self.reset()
        self.read()

        self.next.connect(self.onNext)

    def reset(self):
        self.iterator = -1

    @Slot()
    def onNext(self):
        self.iterator += 1

        #print("HelpR::onSetNext:", self.iterator, self.length)

        if self.iterator < self.length:
            #self.next.emit()
            current = self.data[self.iterator]
            result = []
            for i in current:
                result.append(self.input[i])

            self.currentChanged.emit(result)
        else:
            self.reset()

            self.ready.emit()

        '''
        if not self.data.atEnd():
            self.length += 1
            print("ReadR::onNext:")

            self.readNext.emit(self.getValues())
        else:
            self.length += 1
            print("HelpR::doNext:", self.length)
            self.ready.emit(self.length)
        '''

    def current(self):
        '''
        result = []
        for _ in range(self.config.R):
            result.append(self.data.readUInt8())

        print("HelpR::current:", result)

        return result
        '''

    def read(self):
        def isCurrent(directory, file):
            return file.fileName() == "{directory:s}/{n:d}C{r:d}.{ext:s}".format(directory=directory, n=self.config.N, r=self.config.R, ext=self.config.HELPERS_EXTENSION)

        def hasHeader():
            return file.read(len(self.config.HELPERS_HEADER)).toStdString() == self.config.HELPERS_HEADER

        directory = "{root:s}/{directory:s}".format(root=self.config.ROOT_DIRECTORY, directory=self.config.HELPERS_DIRECTORY)
        for f in [ _ for _ in QDir(directory).entryList() if not _.startswith('.') ]:
            file = QFile("{directory:s}/{filename:s}".format(directory=directory, filename=f))
            if isCurrent(directory, file) and file.open(QIODevice.OpenModeFlag.ReadOnly) and hasHeader():
                #self.data = QDataStream(file)
                data = QDataStream(file)
                if data.readUInt8() == self.config.R:
                    #self.file = file
                    #print("HelpR::read:", self.file.pos())
                    #print("HelpR::read:", self.file, self.current())
                    #self.next.emit(self.current())
                    #self.next.emit()
                    for _ in range(self.length):
                        combination = []
                        for _ in range(self.config.R):
                            combination.append(data.readUInt8())

                        self.data.append(combination)

                    return
                else:
                    file.close()
            else:
                file.close()

    '''
    def write(self):
        if self.output.open(QIODevice.OpenModeFlag.WriteOnly):
            stream = QDataStream(self.output)

            header = self.EXTENSION.upper()[:-1] + str(self.r)
            print(header, len(header))

            stream.writeRawData(QByteArray(self.EXTENSION.upper()[:-1]))
            stream.writeUInt8(self.r)

            for c in list(itertools.combinations(self.n, self.r)):
                for e in c:
                    stream.writeUInt8(e)

            self.output.close()
        else:
            print("Unable to open file to write: {f:s}".format(f=self.output.fileName()))
    '''
