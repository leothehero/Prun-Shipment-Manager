import os
from PyQt6 import QtWidgets, QtCore, uic
from PyQt6.QtGui import QIcon, QColor, QPixmap, QGuiApplication, QStyleHints, QCloseEvent
import sys
import PSMresources

from DSCWidget import DSCWidget
from FleetTracker import FleetTracker
from PrunPythonTools.PRUNDataManager import DataManager, APPDATAFIELD


print("###########################################")
print("#PrUn Shipment Manager [PSM]: v0.1.2 Alpha#")
print("###########################################")

version = "v0.1.2"

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
        cur_dir = os.path.dirname(__file__)
        uic.loadUi(cur_dir+'/ui/PSMMainWindow.ui', self)
        self.theme = QGuiApplication.styleHints().colorScheme().value # 0=unknown 1=light 2=dark
        winIcon = QIcon("icon.png")
        self.setWindowIcon(winIcon) # TODO: Find an Icon

        # Load the PDM
        print("PSM: Loading PDM")
        self.PDM = DataManager({
            "ConfigPath": "PSM.cfg",
            "QtStatusBar": (self.statusBar(),0),
        }, defaultConfig, 4)
        

        # TODO: Fix
        #icon = self.getColouredIcon(cur_dir+"/majesticons-2.1.2/solid/browser.svg") 
        #self.setWindowIcon(icon)

        # Load the DSC
        print("PSM: Loading DSC")
        self.DSCWidget = DSCWidget(PDM=self.PDM)

        # Load the Fleet Tracker
        print("PSM: Loading FLTR")
        self.FleetTracker = FleetTracker(self.PDM)
        self.FLTRWidget.layout().addWidget(self.FleetTracker)

        print("PSM: Main Window initialization complete")

    def showDSC(self):
        self.DSCWidget.hide()
        self.DSCWidget.show()
    
    def getColouredIcon(self,resourceLocator,color='black'): 
        pixmap = QPixmap(resourceLocator)
        #mask = pixmap.createMaskFromColor(QColor('black'), QtCore.Qt.MaskMode.MaskOutColor)
        #pixmap.fill((QColor(color)))
        #pixmap.setMask(mask)
        #return QIcon.fromTheme("network-error")
        return QIcon(pixmap)
    
    def closeEvent(self, event: QCloseEvent):
        print("PSM: Closing! Saving Config State")
        print("PSM: Save Successful" if self.PDM.save() else "PSM: Save Failed")
    

    


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    main = MainWindow()
    main.show()
    app.setStyle('Fusion')
    code = app.exec()
    ()
    sys.exit(code)

if __name__ == '__main__':
    main()
    ()