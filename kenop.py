from PySide6 import QtCore

class Config(QtCore.QObject):
    _instance = None

    def __new__(cls, r, dir):
        if cls._instance is None:
            cls._instance = super().__new__(cls, r, dir)

        return cls._instance

    def __init__(self, r, dir, parent=None):
        #TODO: throw exception if r or dir is None
        super().__init__(parent)

        self._r = r
        self._rootDirectory = dir
        if self._rootDirectory.endswith('/'):
            self._rootDirectory = self._rootDirectory[:-1]

        print(self._r, self._rootDirectory)

        self._n = 20

        self._maxNumberOfYears = 16
        self._numberOfYears = 1

        self._startOfWeeks = 2
        self._endOfWeeks = 50
        self._numberOfWeeks = self._endOfWeeks - self._startOfWeeks + 1

        self._inputsDirectory = "inputs"
        self._inputsExtension = "csv"

        self._helpersDirectory = "helpers"
        self._helpersHeader = "KPNC"
        self._helpersExtension = "kpncr"

        self._resultsDirectory = "R"
        self._resultsHeader = "KPB"
        self._resultsHeaderYearsStart = "Y"
        self._resultsHeaderYearsEnd = "S"
        self._resultsExtension = self._resultsHeader.lower() 

    @property
    def TEMPORARY_EXTENSION(self):
        return ".tmp"

    @property
    def N(self):
        return self._n

    @property
    def R(self):
        return self._r

    @property
    def ROOT_DIRECTORY(self):
        return self._rootDirectory

    @property
    def MAX_NUMBER_OF_YEARS(self):
        return self._maxNumberOfYears

    @property
    def MAX_NUMBER_OF_YEARS_IN_BYTES(self):
        return int(self._maxNumberOfYears/8)

    @property
    def NUMBER_OF_YEARS(self):
        return self._numberOfYears

    @property
    def WEEKS(self):
        return list(range(self._startOfWeeks, self._endOfWeeks + 1))

    @property
    def NUMBER_OF_WEEKS(self):
        return self._numberOfWeeks

    @property
    def START_OF_WEEKS(self):
        return self._startOfWeeks

    @property
    def END_OF_WEEKS(self):
        return self._endOfWeeks

    @property
    def INPUTS_DIRECTORY(self):
        return self._inputsDirectory

    @property
    def INPUTS_EXTENSION(self):
        return self._inputsExtension

    @property
    def HELPERS_DIRECTORY(self):
        return self._helpersDirectory

    @property
    def HELPERS_HEADER(self):
        return self._helpersHeader

    @property
    def HELPERS_EXTENSION(self):
        return self._helpersExtension

    @property
    def RESULTS_DIRECTORY(self):
        return self._resultsDirectory

    @property
    def RESULTS_HEADER(self):
        return self._resultsHeader

    @property
    def RESULTS_HEADER_YEARS_START(self):
        return self._resultsHeaderYearsStart

    @property
    def RESULTS_HEADER_YEARS_END(self):
        return self._resultsHeaderYearsEnd

    @property
    def RESULTS_EXTENSION(self):
        return self._resultsExtension

class KenoP(QtCore.QObject):

    @staticmethod
    def nCr(n, r):
        if r < 0 or n < r :
            return -1

        result = 1
        i = 0
        while i < r :
            i += 1
            result = (result*n)/i
            n -= 1

        return result

    def __init__(self, parent=None):
        super().__init__(parent)

        self.config = Config._instance
