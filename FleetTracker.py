from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QFrame
from PyQt6.QtGui import QGuiApplication, QIntValidator
from PyQt6.QtWidgets import QSizePolicy

import os

class ShipPanel(QWidget):
    def __init__(self,shipInfo): # Assume Transponder/Registration will always be available, as it is the primary key. In the future, I should provide a third argument for custom registrations that aren't in the ship data, cause who knows.
        super().__init__()
        self.registration = shipInfo["Registration"]
        cur_dir = os.path.dirname(__file__)
        uic.loadUi(cur_dir+'/ui/ShipPanel.ui', self)
        self.nameLabel.setText(shipInfo["Name"] if "Name" in shipInfo else "*Name Unavailable*")
        self.transponderLabel.setText(shipInfo["Registration"] if "Registration" in shipInfo else "*Registration Unavailable*")
        self.destinationLabel.setText(shipInfo["Destination"].split(" - ",1)[1] if "Destination" in shipInfo else "*Destination Unavailable*")
        self.usernameLabel.setText(shipInfo["UserNameSubmitted"] if "UserNameSubmitted" in shipInfo else "*Username Unavailable*")

        if "Storage" in shipInfo:
            self.weightBar.setMaximum(int(round(shipInfo["Storage"]["WeightCapacity"],0)))
            self.weightBar.setValue(int(round(shipInfo["Storage"]["WeightLoad"],0)))
            self.volumeBar.setMaximum(int(round(shipInfo["Storage"]["VolumeCapacity"],0)))
            self.volumeBar.setValue(int(round(shipInfo["Storage"]["VolumeLoad"],0)))

        self.configureWidget.hide()
    
    def toggleEditMode(self,state):
        self.configureWidget.setVisible(state)
        #self.routeLabel.setFrameShape(QFrame.Shape.Panel if state else QFrame.Shape.NoFrame)
        #self.routeLabel.released.connect(self.modifyRoute) if state else self.routeLabel.released.disconnect(self.modifyRoute)
    
    def modifyRoute(self):
        print("Modifying Route of Ship "+self.registration)

    def deleteEntry(self):
        print("Deleting Ship Entry "+self.registration)


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
        usernames = set(usernames)
        self.PDM.fetchFleetsByUsers(usernames)

    def displayShips(self):
        for transponder in self.trackedShips:
            self.shipDisplayPanels[transponder] = ShipPanel(self.PDM.getShipData(transponder))
            self.FleetWidget.layout().addWidget(self.shipDisplayPanels[transponder])
            self.configureButton.toggled.connect(self.shipDisplayPanels[transponder].toggleEditMode)
    
    def configureToggle(self,state):
        print(("Entering" if state else "Exiting")+" Fleet Configuration Mode")