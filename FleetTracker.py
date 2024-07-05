from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtGui import QGuiApplication, QIntValidator
from PyQt6.QtWidgets import QSizePolicy

import os

class ShipPanel(QWidget):
    def __init__(self,shipInfo):
        super().__init__()
        cur_dir = os.path.dirname(__file__)
        uic.loadUi(cur_dir+'/ui/ShipPanel.ui', self)
        self.nameLabel.setText(shipInfo["Name"] if "Name" in shipInfo else "*Name Unavailable*")
        self.transponderLabel.setText(shipInfo["Registration"] if "Registration" in shipInfo else "*Registration Unavailable*")
        self.destinationLabel.setText(shipInfo["Destination"].split(" - ",1)[1] if "Destination" in shipInfo else "*Destination Unavailable*")

        if "Storage" in shipInfo:
            self.weightBar.setMaximum(int(round(shipInfo["Storage"]["WeightCapacity"],0)))
            self.weightBar.setValue(int(round(shipInfo["Storage"]["WeightLoad"],0)))
            self.volumeBar.setMaximum(int(round(shipInfo["Storage"]["VolumeCapacity"],0)))
            self.volumeBar.setValue(int(round(shipInfo["Storage"]["VolumeLoad"],0)))

            ()

        self.deleteButton.hide()


class FleetTracker(QWidget):
    trackedShips = {}
    shipDisplayPanels = {}

    def __init__(self,PDM):
        super().__init__()
        self.PDM = PDM
        cur_dir = os.path.dirname(__file__)
        uic.loadUi(cur_dir+'/ui/FleetTracker.ui', self)
        self.loadShips()
        self.displayShips()
    
    def loadShips(self):
        ships = self.PDM.getAppData("ships")
        if not ships:
            return False # TODO: Raise this error higher
        for transponder in ships:
            if ships[transponder]["PSMTracked"]:
                self.trackedShips[transponder] = ships[transponder]
        usernames = []
        # the following section grabs all ships that have a username associated from them, and then tells the PDM to load the fleet data of all those users.
        for transponder in self.trackedShips: #TODO: Move the ship data loading from here to the PDM
            if "Username" in self.trackedShips[transponder]:
                usernames.append(self.trackedShips[transponder]["Username"])
        self.PDM.fetchFleetsByUsers(usernames)

    def displayShips(self):
        for transponder in self.trackedShips:
            self.shipDisplayPanels[transponder] = ShipPanel(self.PDM.getShipData(transponder))
            self.FleetWidget.layout().addWidget(self.shipDisplayPanels[transponder])
    
    def configureToggle(self,state):
        print(("Entering" if state else "Exiting")+" Fleet Configuration Mode")