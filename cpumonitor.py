from PySide6 import QtCore
from PySide6.QtCore import Slot, QProcess, QTimer


class CPUMonitor(QtCore.QObject):
    PROCESS = "top"
    DECODER = "ascii"
    CPU = "CPU"
    CPU_USER = "user"
    CPU_SYSTEM = "sys"
    CPU_IDLE = "idle"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.monitor = QProcess()
        self.monitor.readyReadStandardOutput.connect(self.onTop)

    def get(self):
        self.monitor.start(self.PROCESS, [])

        return self.monitor.waitForFinished()

    def parse(self, output):
        for line in output.split('\n'):
            if line.startswith(self.CPU):
                self.parseCPU(line)
                break

    @Slot()
    def onTop(self):
        self.monitor.terminate()
        self.parse(bytes(self.monitor.readAllStandardOutput()).decode(self.DECODER))

    def parseCPU(self, values):
        result = {}

        def parseValue(property, value):
            if property in value:
                value = value.split('%')
                if len(value) >= 0:
                    result[property] = float(value[0])

        values = values.split(':')
        if len(values) >= 1:
            values = values[1].split(',')
            for value in values:
                parseValue(self.CPU_USER, value)
                parseValue(self.CPU_SYSTEM, value)
                parseValue(self.CPU_IDLE, value)

        return result


