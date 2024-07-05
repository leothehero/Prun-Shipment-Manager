import os
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QIcon, QColor, QPixmap, QGuiApplication, QStyleHints
from qt_material import apply_stylesheet
import sys
import PSMresources

from DSCWidget import DSCWidget
from FleetTracker import FleetTracker
from PrunPythonTools.PRUNDataManager import DataManager, APPDATAFIELD


print("#####################################################")
print("#PrUn Shipment Manager [PSM]: Prototype v0.1.2 Indev#")
print("#####################################################")

defaultConfig = dict({
                "auth": None,
                "group": None,
                APPDATAFIELD: {
                    "ships": {},
                    "contracts":{}
                }, # TODO: detail the data structure of all parameters I use so that other applications can stay in standard.
            })



class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        cur_dir = os.path.dirname(__file__)
        super(MainWindow, self).__init__(*args, **kwargs)
        # self.setGeometry(550, 200, 850, 800)
        self.theme = QGuiApplication.styleHints().colorScheme().value # 0=unknown 1=light 2=dark
        winIcon = QIcon("icon.png")
        self.setWindowIcon(winIcon) # TODO: Find an Icon
        self.setWindowTitle("Prun Shipment Manager [PSM]")

        # Load the PDM
        print("PSM: Loading PDM")
        self.PDM = DataManager({
            "ConfigPath": "PSM.cfg",
            "QtStatusBar": (self.statusBar(),0),
        }, defaultConfig)
        

        # TODO: Fix
        icon = self.getColouredIcon(cur_dir+"/majesticons-2.1.2/solid/browser.svg") 
        self.setWindowIcon(icon)

        # Load the DSC
        print("PSM: Loading DSC")
        self.DSCWidget = DSCWidget(self.PDM)
        self.setCentralWidget(self.DSCWidget)

        # Load the Fleet Tracker
        print("PSM: Loading FLTR")
        self.FleetTracker = FleetTracker(self.PDM)
        self.FleetTracker.show()

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
    app.setStyle('Fusion')
    #apply_stylesheet(app, theme='dark_medical.xml')
    #app.palette().setCurrentColorGroup(QColor.darker())
    code = app.exec()
    ()
    sys.exit(code)

if __name__ == '__main__':
    main()
    ()