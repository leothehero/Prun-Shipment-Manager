from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QFrame
from PyQt6.QtCore import QDateTime, QTimer

import os

def decodeLocation(location):
    system, subLocation = location.split(" - ")
    system = system.rsplit(" ",1)
    subLocation = subLocation.rsplit(" ",1)
    return system, subLocation

class ShipPanel(QWidget):
    # TODO: Have a toggle between "Arrival Time" and "Time To Arrival"
    def __init__(self,shipInfo, PDM): # Assume Transponder/Registration will always be available, as it is the primary key. In the future, I should provide a third argument for custom registrations that aren't in the ship data, cause who knows.
        super().__init__()
        self.PDM = PDM
        self.registration = shipInfo["Registration"]
        cur_dir = os.path.dirname(__file__)
        uic.loadUi(cur_dir+'/ui/ShipPanel.ui', self)
        self.nameLabel.setText(shipInfo["Name"] if "Name" in shipInfo else "*Name Unavailable*")
        self.transponderLabel.setText(shipInfo["Registration"] if "Registration" in shipInfo else "*Registration Unavailable*")
        
        destination = "*Destination Unavailable*"
        if "Destination" in shipInfo:
            system, subLocation = decodeLocation(shipInfo["Destination"])
            destination = subLocation[0] if len(system) == 1 else (system[0] + " - " + subLocation[0].title())
        self.destinationLabel.setText(destination)

        location = "*Location Unavailable*"
        self.arrivalTime.setFrame(True)
        if "Location" in shipInfo:
            if shipInfo["Location"] == '':  # Ship is in transit
                location = "**Traversing the Void**"
            else: # Ship has arrived at a Location
                self.arrivalTime.setFrame(False)
                self.locationLabel.setFrameShape(QFrame.Shape.Box)
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.showTime)
                self.timer.start(1000)
                self.showTime()
                system, subLocation = decodeLocation(shipInfo["Location"])
                location = subLocation[0] if len(system) == 1 else (system[0] + " - " + subLocation[0].title())
                #location = "<mark>"+location+"</mark>"
        self.locationLabel.setText(location)
        userData = self.PDM.getUserInfo(shipInfo["UserNameSubmitted"] if "UserNameSubmitted" in shipInfo else "")
        username = userData["UserName"] if "UserName" in userData else "*Username Unavailable*"
        self.usernameLabel.setText(username)

        if "Storage" in shipInfo:
            self.weightBar.setMaximum(int(round(shipInfo["Storage"]["WeightCapacity"],0)))
            self.weightBar.setValue(int(round(shipInfo["Storage"]["WeightLoad"],0)))
            self.volumeBar.setMaximum(int(round(shipInfo["Storage"]["VolumeCapacity"],0)))
            self.volumeBar.setValue(int(round(shipInfo["Storage"]["VolumeLoad"],0)))

        if "ArrivalTimeEpochMs" in shipInfo:
            #self.arrivalTime.setDisplayFormat("HH:mm dddd")
            time = QDateTime()
            time.setMSecsSinceEpoch(shipInfo["ArrivalTimeEpochMs"])
            self.arrivalTime.setDateTime(time)

        self.configureWidget.hide()
    
    def toggleEditMode(self,state):
        self.configureWidget.setVisible(state)
        #self.routeLabel.setFrameShape(QFrame.Shape.Panel if state else QFrame.Shape.NoFrame)
        #self.routeLabel.released.connect(self.modifyRoute) if state else self.routeLabel.released.disconnect(self.modifyRoute)
    
    def modifyRoute(self):
        print("Modifying Route of Ship "+self.registration)

    def deleteEntry(self):
        print("Deleting Ship Entry "+self.registration)

    def showTime(self):
            time = QDateTime.currentDateTime()
            self.arrivalTime.setDateTime(time)



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
            self.shipDisplayPanels[transponder] = ShipPanel(self.PDM.getShipData(transponder),self.PDM)
            self.FleetWidget.layout().addWidget(self.shipDisplayPanels[transponder])
            self.configureButton.toggled.connect(self.shipDisplayPanels[transponder].toggleEditMode)
    
    def configureToggle(self,state):
        print(("Entering" if state else "Exiting")+" Fleet Configuration Mode")