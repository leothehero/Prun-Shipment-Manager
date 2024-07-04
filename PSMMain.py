import os
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QIcon, QColor, QPixmap, QGuiApplication

import sys
import PSMresources

from DSCWidget import DSCWidget
from FleetTracker import FleetTracker
from PrunPythonTools.PRUNDataManager import DataManager


print("###############################################################")
print("#PrUn Shipment Manager [PSM]: Prototype Major Build 1 - v0.1.1#")
print("###############################################################")


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        cur_dir = os.path.dirname(__file__)
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setGeometry(550, 200, 850, 800)
        self.theme = QGuiApplication.styleHints().colorScheme().value # 0=unknown 1=light 2=dark
        winIcon = QIcon("icon.png")
        self.setWindowIcon(winIcon) # TODO: Find an Icon
        self.setWindowTitle("Prun Shipment Manager [PSM]")

        # Load the PDM
        self.PDM = DataManager({
            "ConfigPath": "PSM.cfg",
            "QtStatusBar": (self.statusBar(),0),
        })
        icon = self.getColouredIcon(cur_dir+"/majesticons-2.1.2/solid/browser.svg")
        self.setWindowIcon(icon)

        # Load the DSC
        self.DSCWidget = DSCWidget(self.PDM)
        self.setCentralWidget(self.DSCWidget)

        ()
    
    def getColouredIcon(self,resourceLocator,color='black'): 
        pixmap = QPixmap(resourceLocator)
        #mask = pixmap.createMaskFromColor(QColor('black'), QtCore.Qt.MaskMode.MaskOutColor)
        #pixmap.fill((QColor(color)))
        #pixmap.setMask(mask)
        #return QIcon.fromTheme("network-error")
        return QIcon(pixmap)
    

    


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    code = app.exec()
    ()
    sys.exit(code)

if __name__ == '__main__':
    main()
    ()