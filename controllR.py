import itertools

from kenop import KenoP

from PySide6.QtCore import Signal, Slot, QDir, QTimer, QByteArray, QThread

#from cpumonitor import CPUMonitor
#outputhandler import OutputHandler

from drawHelpR import DrawHelpR
from readR import ReadR
from writR import WritR


class ControllR(KenoP):
    '''
    CPU_THRESHOLD = 50
    CPU_TIMEOUT = 3000
    '''

    readLine = Signal()
    setData = Signal(list)
    nextCombination = Signal(list)
    combinationReady = Signal()
    nextHelper = Signal()

    readNextHelpR = Signal()
    doNextHelpR = Signal()

    readerThread = QThread()
    writerThread = QThread()

    def __init__(self, parent=None):
        super().__init__(parent)

        #self.monitor = CPUMonitor()
        #self.output = OutputHandler(self)

        self.readerThread.started.connect(self.setWriter)
        self.writerThread.started.connect(lambda: self.reader.read())

        self.setInputs()

        self.drawHelper = DrawHelpR()
        self.drawHelper.setNext.connect(self.onDrawHelperSetNext)
        self.drawHelper.ready.connect(self.onDrawHelperReady)

        self.reader = ReadR(self.inputs)
        self.reader.moveToThread(self.readerThread)
        self.reader.next.connect(self.onReaderNext)
        self.reader.dataChanged.connect(self.onReaderDataChanged)
        self.reader.ready.connect(self.onReaderReady)
        self.readerThread.start()

    def setInputs(self):
        inputs = list(filter(lambda _: not _.startswith('.'), QDir("{root:s}/{inputs:s}".format(root=self.config.ROOT_DIRECTORY, inputs=self.config.INPUTS_DIRECTORY)).entryList('*.' + self.config.INPUTS_EXTENSION)))
        inputs.sort(reverse=True)

        #TODO: read year from file
        self.inputs = list(map(lambda _: (_, int(_.split('.')[0])), inputs[:self.config.NUMBER_OF_YEARS] if len(inputs) >= self.config.NUMBER_OF_YEARS else inputs))

    @Slot()
    def setWriter(self):
        self.writer = WritR(self.inputs)
        self.writer.moveToThread(self.writerThread)
        self.writer.checkAndSetNext.connect(self.onWriterCheckAndSetNext)
        self.writer.checkAndSetReady.connect(self.onWriterCheckAndSetReady)

        self.writerThread.start()

    @Slot()
    def onReaderNext(self):
        self.reader.readNextLine.emit()

    @Slot()
    def onReaderDataChanged(self):
        print("ControllR::onReaderDataChanged:", self.reader.year, self.reader.week, self.reader.data)
        #self.writer.openFile()
        #self.writer.openTemporaryFile()

        self.drawHelper.read()

    @Slot()
    def onReaderReady(self):
        #self.writer.close()
        print("ControllR::onReaderReady: ready")

    @Slot(list)
    def onDrawHelperSetNext(self, values):
        combination = []
        for i in values:
            combination.append(self.reader.data[i])

        #print("ControllR::onHelpersetNext:", combination)
        self.writer.write.emit(self.reader.year, self.reader.week, combination)

    @Slot()
    def onDrawHelperReady(self):
        #print("ControllR::onHelperReady")
        self.reader.readNextLine.emit()

    @Slot()#(int, QByteArray)
    def onWriterCheckAndSetNext(self):#, position, combination)
        #print("ConrolR::onWriterCheckAndSetNext", position, combination)
        #self.writer.checkAndSet.emit(position, combination)
        self.drawHelper.next.emit()

    @Slot()#(QByteArray)
    def onWriterCheckAndSetReady(self):
        '''
        #print(self.writer.state)

        if self.writer.state == WritR.State.EXISTING:
            self.writer.openFile()
            self.writer.openTemporaryFile()

        print("ControllR::onWriterCheckAndSetReady:", self.writer.state, c)
        '''
        pass


    '''
    @Slot()
    def onWriterNext(self):
        print("writer next")
        #self.writer.file.close()
    '''
