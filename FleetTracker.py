from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QFrame, QDialog
from PyQt6.QtCore import QDateTime, QTimer
from PyQt6.QtGui import QValidator

import os, re


def decodeLocation(location): # TODO: Move to PDM
    system, subLocation = location.split(" - ")
    system = system.rsplit(" ",1)
    subLocation = subLocation.rsplit(" ",1)
    return system, subLocation

class LocationValidator(QValidator):
    def __init__(self,PDM):
        super().__init__()
        self.PDM = PDM
    
    def validate(self,stringArg,intArg):
        tmpStr = re.split(r'[,;]',stringArg)
        valid = True
        for i in range(len(tmpStr)):
            tmpStr[i] = tmpStr[i].strip()
            valid = valid and self.PDM.isLocation(tmpStr[i])

        print(tmpStr, valid)
        return QValidator.State.Acceptable if valid else QValidator.State.Intermediate, stringArg, intArg


class ShipDialog(QDialog):
    def __init__(self, PDM, parent=None):
        super().__init__(parent)
        cur_dir = os.path.dirname(__file__)
        uic.loadUi(cur_dir+'/ui/ShipDialog.ui', self)
        self.routeAddBox.setValidator(LocationValidator(PDM))
        self.shipTransponderEdit.setFocus()

    def loadData(self, shipInfo):
        self.shipTransponderEdit.setText(shipInfo["Registration"] if "Registration" in shipInfo else "")
        self.shipUsernameEdit.setText(shipInfo["UserNameSubmitted"] if "UserNameSubmitted" in shipInfo else "")

def handler(self): # THIS WORKS!!!
    print("test")

class ShipPanel(QWidget):
    # TODO: Have a toggle between "Arrival Time" and "Time To Arrival"
    def __init__(self,shipInfo, PDM): # Assume Transponder/Registration will always be available, as it is the primary key. In the future, I should provide a third argument for custom registrations that aren't in the ship data, cause who knows.
        super().__init__()
        self.PDM = PDM
        self.shipInfo = shipInfo
        self.registration = self.shipInfo["Registration"]
        cur_dir = os.path.dirname(__file__)
        uic.loadUi(cur_dir+'/ui/ShipPanel.ui', self)

        self.setNameLabel()
        self.setTransponderLabel()
        self.setDestinationLabel()
        self.setLocationLabel()
        self.setUsernameLabel()

        self.setStorageBars()
        self.setArrivalTime()
        
        self.routeLabel.mousePressEvent = handler # THIS WORKS!!!

    def modifyEntry(self):
        print("SP: Modifying Entry of ship "+self.registration)
        dialog = ShipDialog(self.PDM, self)
        dialog.loadData(self.shipInfo)
        dialog.exec()

        return

    def setArrivalTime(self):
        if "ArrivalTimeEpochMs" in self.shipInfo:
            #self.arrivalTime.setDisplayFormat("HH:mm dddd")
            time = QDateTime()
            time.setMSecsSinceEpoch(self.shipInfo["ArrivalTimeEpochMs"])
            self.arrivalTime.setDateTime(time)

    def setStorageBars(self):
        if "Storage" in self.shipInfo:
            self.weightBar.setMaximum(int(round(self.shipInfo["Storage"]["WeightCapacity"],0)))
            self.weightBar.setValue(int(round(self.shipInfo["Storage"]["WeightLoad"],0)))
            self.volumeBar.setMaximum(int(round(self.shipInfo["Storage"]["VolumeCapacity"],0)))
            self.volumeBar.setValue(int(round(self.shipInfo["Storage"]["VolumeLoad"],0)))

    def setUsernameLabel(self):
        userData = self.PDM.getUserInfo(self.shipInfo["UserNameSubmitted"] if "UserNameSubmitted" in self.shipInfo else "")
        username = userData["UserName"] if "UserName" in userData else "*Username Unavailable*"
        self.usernameLabel.setText(username)

    def setNameLabel(self):
        self.nameLabel.setText(self.shipInfo["Name"] if "Name" in self.shipInfo else "*Name Unavailable*")

    def setTransponderLabel(self):
        self.transponderLabel.setText(self.shipInfo["Registration"] if "Registration" in self.shipInfo else "*Registration Unavailable*")

    def setDestinationLabel(self):
        destination = "*Destination Unavailable*"
        if "Destination" in self.shipInfo:
            system, subLocation = decodeLocation(self.shipInfo["Destination"])
            destination = subLocation[0] if len(system) == 1 else (system[0] + " - " + subLocation[0].title())
        self.destinationLabel.setText(destination)

    def setLocationLabel(self):
        location = "*Location Unavailable*"
        self.arrivalTime.setFrame(True)
        if "Location" in self.shipInfo:
            if self.shipInfo["Location"] == '':  # Ship is in transit
                location = "**Traversing the Void**"
            else: # Ship has arrived at a Location
                self.arrivalTime.setFrame(False)
                self.locationLabel.setFrameShape(QFrame.Shape.Box)
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.showTime)
                self.timer.start(1000)
                self.showTime()
                system, subLocation = decodeLocation(self.shipInfo["Location"])
                location = subLocation[0] if len(system) == 1 else (system[0] + " - " + subLocation[0].title())
                #location = "<mark>"+location+"</mark>"
        self.locationLabel.setText(location)

        #self.configureWidget.hide()
    
    def toggleEditMode(self,state):
        self.configureWidget.setVisible(state)
        #self.routeLabel.setFrameShape(QFrame.Shape.Panel if state else QFrame.Shape.NoFrame)
        #self.routeLabel.released.connect(self.modifyRoute) if state else self.routeLabel.released.disconnect(self.modifyRoute)
    
    def deleteEntry(self):
        print("SP: Deleting Entry of Ship "+self.registration)

    def showTime(self):
            time = QDateTime.currentDateTime()
            self.arrivalTime.setDateTime(time)



class FleetTracker(QWidget):
    trackedShips = {}
    shipDisplayPanels = {}

    def __init__(self, PDM, parent=None):
        super().__init__(parent)
        self.PDM = PDM
        cur_dir = os.path.dirname(__file__)
        uic.loadUi(cur_dir+'/ui/FleetTracker.ui', self)
        self.loadShips()
        self.displayShips()
        PDM.fetchPlanetNameData()
        PDM.fetchStationData()
    
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
    
    def addShip(self):
        dialog = ShipDialog(self.PDM, self)
        dialog.exec()
        #ships = self.PDM.getAppData("ships") or {}

    def displayShips(self):
        for transponder in self.trackedShips:
            self.shipDisplayPanels[transponder] = ShipPanel(self.PDM.getShipData(transponder),self.PDM)
            self.FleetWidget.layout().addWidget(self.shipDisplayPanels[transponder])
    
    def configureToggle(self,state):
        print(("Entering" if state else "Exiting")+" Fleet Configuration Mode")