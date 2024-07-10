from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QFrame, QDialog
from PyQt6.QtCore import QDateTime, QTimer, Qt
from PyQt6.QtGui import QValidator

import os, re

from PrunPythonTools import PRUNDataManager


def decodeLocation(location): # TODO: Move to PDM
    system, subLocation = location.split(" - ")
    system = system.rsplit(" ",1)
    subLocation = subLocation.rsplit(" ",1)
    return system, subLocation

class LocationValidator(QValidator):
    def __init__(self,PDM):
        super().__init__()
        self.PDM = PDM
    
    def validate(self,stringArg: str,intArg: str) -> tuple[QValidator.State]:
        tmpStr, valid = self.format(stringArg)
        #NOTE: Temporary Idea for autoformatting, remove or optimise if the performance cost is exorbitant.
        if valid:
            for i in range(len(tmpStr)):
                if self.PDM.isStation(tmpStr[i])[0]:
                    tmpStr[i] = self.PDM.getStationNameFormat(tmpStr[i])
                elif True in self.PDM.isPlanet(tmpStr[i]):
                    tmpStr[i] = self.PDM.getPlanetNameFormat(tmpStr[i])
            stringArg = ", ".join(tmpStr)
        return QValidator.State.Acceptable if valid else QValidator.State.Intermediate, stringArg, intArg

    def format(self, stringArg: str) -> tuple[list[str] , bool]:
        tmpStr = re.split(r'[,;]',stringArg)
        valid = True
        for i in range(len(tmpStr)):
            tmpStr[i] = tmpStr[i].strip()
            valid = valid and self.PDM.isLocation(tmpStr[i])
        return tmpStr,valid


class ShipDialog(QDialog):
    def __init__(self, PDM, parent=None):
        super().__init__(parent)
        cur_dir = os.path.dirname(__file__)
        uic.loadUi(cur_dir+'/ui/ShipDialog.ui', self)
        self.validator = LocationValidator(PDM)
        self.routeAddBox.setValidator(self.validator)
        self.shipTransponderEdit.setFocus()

    def showEvent(self, event): # This prevents any button from being a default button
        for button in self.buttonBox.buttons():
            button.setAutoDefault(False)
            button.setDefault(False)

    def loadData(self, shipInfo: dict):
        self.shipTransponderEdit.setText(shipInfo["Registration"] if "Registration" in shipInfo else "")
        self.shipUsernameEdit.setText(shipInfo["UserNameSubmitted"] if "UserNameSubmitted" in shipInfo else "")
        self.routeList.addItems(shipInfo["Route"] if "Route" in shipInfo else ())
        self.setItemsEditable()
        #self.routeList.connect


    def addLocations(self):
        tmpStr, valid = self.validator.format(self.routeAddBox.text())
        if not valid:
            raise ValueError
        self.routeList.addItems(tmpStr)
        #self.setItemsEditable()
        self.routeAddBox.clear()
    
    def getRouteListItems(self):
        items = []
        for i in range(self.routeList.count()):
            items.append(self.routeList.item(i))
        return items

    def setItemsEditable(self):
        for item in self.getRouteListItems():
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)

def handler(self): # THIS WORKS!!!
    print("test")

class ShipPanel(QWidget):
    modified = False
    dateTimeFormat = "hh:mm   dddd"
    # TODO: Have a toggle between "Arrival Time" and "Time To Arrival"
    def __init__(self,shipInfo, PDM): # Assume Transponder/Registration will always be available, as it is the primary key. In the future, I should provide a third argument for custom registrations that aren't in the ship data, cause who knows.
        super().__init__()
        self.PDM = PDM
        self.shipInfo = shipInfo
        self.registration = self.shipInfo["Registration"]
        cur_dir = os.path.dirname(__file__)
        uic.loadUi(cur_dir+'/ui/ShipPanel.ui', self)
        self.arrivalTime = QDateTime()

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
        self.dialog = ShipDialog(self.PDM, self)
        self.dialog.loadData(self.shipInfo)
        self.dialog.open()
        self.dialog.accepted.connect(self.acceptDialog)
        return
    
    def acceptDialog(self):
        items = self.dialog.getRouteListItems()
        routeItems = []
        for item in items:
            routeItems.append(item.text())
        self.shipInfo["Route"] = routeItems
        self.updateRouteDisplay()
        self.modified = True # TODO: Change this to just call a parent update function. Reuse between this and the Parent acceptDialog()

    def updateRouteDisplay(self):
        if "Route" not in self.shipInfo or len(self.shipInfo["Route"]) == 0:
            self.routeLabel.setText("No **Route** Set")
            return
        contents = " -> ".join(self.shipInfo["Route"]) + " -> ..."
        self.routeLabel.setText(contents)
        return

    def setArrivalTime(self):
        if "ArrivalTimeEpochMs" in self.shipInfo:
            #self.arrivalTime.setDisplayFormat("HH:mm dddd")
            time = QDateTime()
            self.arrivalTime.setMSecsSinceEpoch(self.shipInfo["ArrivalTimeEpochMs"])
            text = self.arrivalTime.toString(self.dateTimeFormat)
            self.arrivalLabel.setText(text)


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
        if "Location" in self.shipInfo:
            if self.shipInfo["Location"] == '':  # Ship is in transit
                location = "**Traversing the Void**"
            else: # Ship has arrived at a Location
                self.arrivalLabel.setText("**Arrived**")
                self.locationLabel.setFrameShape(QFrame.Shape.Box)
                system, subLocation = decodeLocation(self.shipInfo["Location"])
                location = subLocation[0] if len(system) == 1 else (system[0] + " - " + subLocation[0].title())
                #location = "<mark>"+location+"</mark>"
        self.locationLabel.setText(location)
        
    def deleteEntry(self):
        print("SP: Deleting Entry of Ship "+self.registration)
        raise NotImplementedError

    def showTime(self): # Unused
            time = QDateTime.currentDateTime()
            self.arrivalTime.setDateTime(time)



class FleetTracker(QWidget):
    trackedShips = {}
    shipDisplayPanels = {}

    def __init__(self, PDM: PRUNDataManager.DataManager, parent=None): 
        super().__init__(parent)
        self.PDM = PDM
        cur_dir = os.path.dirname(__file__)
        uic.loadUi(cur_dir+'/ui/FleetTracker.ui', self)
        self.loadShips()
        self.displayShips()
        PDM.fetchPlanetNameData() # TODO: switch to initX methods
        PDM.fetchStationData()
        PDM.fetchUserList()
    
    def loadShips(self) -> bool: 
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
        return True
    
    def addShip(self):
        self.dialog = ShipDialog(self.PDM, self)
        self.dialog.open()
        self.dialog.accepted.connect(self.acceptDialog)

    def displayShips(self):
        for transponder in self.trackedShips:
            shipData = self.PDM.getShipData(transponder)
            if not shipData:
                shipData = {
                    "Registration": transponder,
                    "UserNameSubmitted": self.trackedShips[transponder]["Username"]
                }
            self.shipDisplayPanels[transponder] = ShipPanel(shipData,self.PDM)
            self.FleetWidget.layout().addWidget(self.shipDisplayPanels[transponder])
    
    def acceptDialog(self):
        items = self.dialog.getRouteListItems()
        routeItems = []
        for item in items:
            routeItems.append(item.text())
        # Create verification function to make sure the resultant fields are valid!