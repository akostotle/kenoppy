import sys

from kenop import Config

from PySide6.QtWidgets import QApplication
#from PySide6.QtCore import QDir, QBitArray

from controllR import ControllR

#from combinations import Combinations

#from outputhandler import OutputHandler

if __name__ == "__main__":
    app = QApplication(sys.argv)

    r = None
    dir = None
    #TODO: years
    y = None

    length = len(sys.argv)
    if length > 1 and length%2 == 1:
        i = 1
        while(i<length):
            if sys.argv[i] == "-r":
                r = int(sys.argv[i+1])
            elif sys.argv[i] == "-d":
                dir = sys.argv[i+1]

            i += 2

        Config(r, dir)

        controller = ControllR()
    else:
        #TODO: throw exception if sys.argv is wrong
        pass

    #controller = ControllR(2)
    #controller.read()
    #print(controller.combinations.nCr(20, 2, True))

    sys.exit(app.exec())
