import itertools

from PySide6 import QtCore
from PySide6.QtCore import Signal, Slot, QTimer, QFile

#from cpumonitor import CPUMonitor


class Combinations(QtCore.QObject):
    nextCombination = Signal(int)
    nextCombinationReady = Signal(int)
    nextCombinationUtil = Signal(int, bool)
    ready = Signal()

    @staticmethod
    def nCr(n, r, mustBeSaved=False):
        if r < 0 or n < r :
            return -1

        result = 1
        i = 0
        while i < r :
            i += 1
            result = (result*n)/i
            n -= 1

        return result

        '''
        combinations = list(itertools.combinations(n, r))
        if mustBeSaved:
            output = QFile("kpncrs/{n:d}C{r:d}.kpncrs".format(n=n, r=r))
            print(output.fileName())

        return len(combinations)
        '''

    def __init__(self, input = None, parent=None):
        super().__init__(parent)

        self.nextCombination.connect(self.onNextCombination)
        self.nextCombinationReady.connect(self.onNextCombinationReady)
        self.nextCombinationUtil.connect(self.onNextCombinationUtil)

        self.index = -1
        self.result = []

        self.counter = 0 

    def set(self, input):
        #self.input = input
        self.input = [1, 2, 3, 4]
        self.n = len(self.input)
        self.data = []

    def do(self, r):
        self.r = r
        self.length = self.nCr(self.n, self.r)
        self.iteration = 0

        self.combinationUtil();

    def combinationUtil(self, index=0):
        print("Combinations::combinationUtil", self.data, index, len(self.result))
        '''
        if len(self.data) == self.r:
            self.result.append(list(self.data))

            if len(self.result) == self.length:
                self.ready.emit()

            return
        '''

        if index >= self.n:
            print("--- SET ---")
            self.set(self.input[1:])

            index = 0
            #return

        #self.counter += 1
        #if self.counter % 8 == 0:
            #self.monitor.get()

        # TODO: ide???

        self.nextCombination.emit(index)

    @Slot()
    def next(self):
        self.data.pop(),
        self.combinationUtil(self.index + 1)

    @Slot(int)
    def onNextCombination(self, index):
        print("Combinations::onNextCombination", index, self.data)
        if len(self.input) > 0:
            self.data.append(self.input[index])
            if len(self.data) == self.r:
                #print("Combinations::onNextCombination", self.data)
                self.nextCombinationReady.emit(index)
            else:
                self.nextCombinationUtil.emit(index, False)
                '''
                self.combinationUtil(index + 1)

                if len(self.data) > 0:
                    self.data.pop()
                    self.combinationUtil(index + 1)
                '''
        else:
            self.ready.emit()

    @Slot(int)
    def onNextCombinationReady(self, index):
        print("Combinations::onNextCombinationReady", self.data, index)
        # TODO: CPUMonitor???
        self.result.append(list(self.data))
        self.iteration += 1

        #if len(self.result) == self.length:
        if self.iteration == self.length:
            self.ready.emit()
        else:
            self.index = index

            '''
            QTimer.singleShot(50, lambda : (
                self.data.pop(),
                self.combinationUtil(index + 1)
            ))
            '''
            QTimer.singleShot(5, self.next)

    @Slot(int)
    def onNextCombinationUtil(self, index):#, hasData):
        #print("Combinations::onNextCombinationUtil", index)
        # TODO: CPUMonitor???
        #if not hasData:
        self.combinationUtil(index + 1)
        '''
        elif len(self.data) > 0:
            #self.data.pop()
            self.combinationUtil(index + 1)
            #self.nextCombinationUtil.emit(index + 1, True)
        '''
