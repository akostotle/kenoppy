import itertools

from kenop import KenoP

from PySide6.QtCore import Signal, Slot, QDir, QThread

from cpumonitor import CPUMonitor
#outputhandler import OutputHandler

from helpR import HelpR
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

    HRT = QThread() #TODO: redefine to HRT
    RRT = QThread() #TODO: redefine to RRT
    WRT = QThread() #TODO: redefine to WRT

    WCT = QThread() # WeeklyCombinationThread

    def __init__(self, parent=None):
        super().__init__(parent)

        self.monitor = CPUMonitor()
        #self.output = OutputHandler(self)

        self.setInputs()

        self.helper = HelpR()
        self.helper.currentChanged.connect(self.onHelperCurrentChanged)
        self.helper.ready.connect(self.onHelperReady)
        self.helper.moveToThread(self.HRT)
        self.HRT.started.connect(lambda: self.RRT.start())

        self.reader = ReadR(self.inputs)
        self.reader.next.connect(self.onReaderNext)
        self.reader.dataChanged.connect(self.onReaderDataChanged)
        self.reader.ready.connect(self.onReaderReady)
        self.reader.moveToThread(self.RRT)
        self.RRT.start()

        self.RRT.started.connect(self.setWriter)
        self.WRT.started.connect(lambda: self.reader.read())

        self.HRT.start()

    def setInputs(self):
        inputs = list(filter(lambda _: not _.startswith('.'), QDir("{root:s}/{inputs:s}".format(root=self.config.ROOT_DIRECTORY, inputs=self.config.INPUTS_DIRECTORY)).entryList('*.' + self.config.INPUTS_EXTENSION)))
        inputs.sort(reverse=True)

        #TODO: read year from file
        self.inputs = list(map(lambda _: (_, int(_.split('.')[0])), inputs[:self.config.NUMBER_OF_YEARS] if len(inputs) >= self.config.NUMBER_OF_YEARS else inputs))

    @Slot()
    def setWriter(self):
        self.writer = WritR(self.monitor, self.inputs)
        self.writer.checkAndSetNext.connect(self.onWriterCheckAndSetNext)
        self.writer.checkAndSetReady.connect(self.onWriterCheckAndSetReady)
        self.writer.moveToThread(self.WRT)
        self.WRT.start()

    '''
    @Slot(list)
    def onHelperNext(self):
    #@Slot()
    #def onHelperNext(self):
        values = self.helper.current()

        combination = []
        for i in values:
            combination.append(self.reader.data[i])

        print("ControllR::onHelperNext:", self.reader.data, values, combination)
    '''

    @Slot(list)
    def onHelperCurrentChanged(self, values):
        #print("ControllR::onHelperCurrentChanged:", values, self.writer.combinations.week)
        self.writer.combinations.append(values)
        self.helper.next.emit()
        #self.reader.readNextLine.emit()

    @Slot()
    def onHelperReady(self):
        #print("ControllR::onHelperReady:", self.writer.combinations.length())

        self.reader.setNextLine.emit()

    @Slot()
    def onReaderNext(self):
        #print("ControllR::onReaderNext:")
        #self.reader.readNext.emit()
        self.reader.setNext.emit()
        #pass

    @Slot()
    def onReaderDataChanged(self):
        print("ControllR::onReaderDataChanged:", self.reader.year, self.reader.week, self.reader.day, self.reader.data)

        self.writer.combinations.week = self.reader.week
        self.helper.input = self.reader.data

        #self.reader.setNext.emit()
        self.helper.next.emit()

    @Slot()
    def onReaderReady(self):
        #self.writer.close()
        print("ControllR::onReaderReady:", self.writer.combinations.size())

        '''
        i = 0
        while i < len(self.writer.combinations.combinations):
            print(self.writer.combinations.combinations[i])
            i += 1
        '''

        '''
        if not self.WCT.isRunning():
            self.WCT.started.connect(lambda: print("starte:", self.WCT))
            self.WCT.start()
        '''

        self.writer.combinations.clear()

        print("ControllR::onReaderReady:", self.writer.combinations.size())

        #self.helper.next.emit()

        #if self.reader.inputsIterator < self.config.NUMBER_OF_YEARS:
        #self.reader.readNextLine.emit()

    @Slot()#(int, QByteArray)
    def onWriterCheckAndSetNext(self):#, position, combination)
        #print("ConrolR::onWriterCheckAndSetNext", position, combination)
        #self.writer.checkAndSet.emit(position, combination)
        self.helper.next.emit()

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

    @Slot()
    def onSaveCurrentWeek(self):
        self.writer.currentWeek = self.writer.week
        print("ControlR::onSaveCurrentWeek:", self.writer.currentWeek)

        self.writer.close()
        if self.writer.openFile(False):
            self.reader.next.emit()

    '''
    @Slot()
    def onWriterNext(self):
        print("writer next")
        #self.writer.file.close()
    '''
