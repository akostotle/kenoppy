from kenop import KenoP
from PySide6.QtCore import Signal, Slot, QIODevice, QFile


class ReadR(KenoP):
    next = Signal()
    readNextLine = Signal()
    dataChanged = Signal()
    ready = Signal()

    def __init__(self, inputs):
        super().__init__()

        self.inputs = list(map(lambda _: "{root:s}/{dir:s}/{file:s}".format(root=self.config.ROOT_DIRECTORY, dir=self.config.INPUTS_DIRECTORY, file=_[0]), inputs))
        self.inputsIterator = 0

        self.year = -1
        self.week = -1
        self.data = []

        self.readNextLine.connect(self.onNext)

        #self.read()

    def read(self):
        self.input = QFile(self.inputs[self.inputsIterator])
        print("ReadR::read:", self.input.fileName())
        if self.input.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
            self.readLine()

    def readLine(self):
        if not self.input.atEnd():
            self.parse(self.input.readLine())
        else:
            print("ReadR::readLine: atEnd and close")
            self.input.close()

            self.ready.emit()

    def parse(self, values):
        if values.endsWith('\n'):
            values = values[:-1]

        #print("ReadR::parse:", values)

        p = values.split(';')
        if len(p) >= (4 + self.config.N):
            self.year = int(p[0])
            self.week = int(p[1])
            self.data = []

            #if self.week >= self.config.START_OF_WEEKS and self.week <= self.config.END_OF_WEEKS:
            #if self.week >= self.config.END_OF_WEEKS - 1 and self.week <= self.config.END_OF_WEEKS:
            if self.week <= self.config.END_OF_WEEKS and self.week >= self.config.END_OF_WEEKS:# - 1:
                for i in range(4, len(p)):
                    self.data.append(int(p[i]))

                print("ReadR::parse:", self.dTA)
                #self.dataChanged.emit() if (int(p[2]) == 7 or int(p[2]) == 6) else self.next.emit()
                #self.dataChanged.emit()
            else:
                self.next.emit()
        else:
            self.next.emit()

    @Slot()
    def onNext(self):
        self.readLine()

