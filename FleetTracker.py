from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QFrame, QDialog, QDialogButtonBox
from PyQt6.QtCore import QDateTime, QTimer, Qt
from PyQt6.QtGui import QValidator

import os, re

from PrunPythonTools.PRUNDataManager import DataManager as PrUnDM


def decodeLocation(location): # TODO: Move to PDM
    system, subLocation = location.split(" - ")
    system = system.rsplit(" ",1)
    subLocation = subLocation.rsplit(" ",1)
    return system, subLocation

class LocationValidator(QValidator):
    valid = False
    
    def __init__(self, PDM:PrUnDM):
        super().__init__()
        self.PDM = PDM
    
    def validate(self,stringArg: str,intArg: str) -> tuple[QValidator.State, str, int]:
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

class UserValidator(QValidator):
    valid = False

    def __init__(self, PDM:PrUnDM):
        super().__init__()
        self.PDM = PDM

    def validate(self,stringArg: str,intArg: str) -> tuple[QValidator.State, str, int]:
        tmpStr = stringArg.strip()
        valid, formattedUsername = self.PDM.isUser(tmpStr)
        self.valid = valid
        return QValidator.State.Acceptable if valid else QValidator.State.Intermediate, formattedUsername, intArg

class ShipDialog(QDialog):
    validRoute = False

    def __init__(self, PDM, parent=None):
        super().__init__(parent)
        cur_dir = os.path.dirname(__file__)
        uic.loadUi(cur_dir+'/ui/ShipDialog.ui', self)
        self.lValidator = LocationValidator(PDM)
        self.uValidator = UserValidator(PDM)
        self.routeAddBox.setValidator(self.lValidator)
        self.shipUsernameEdit.setValidator(self.uValidator)
        self.shipTransponderEdit.setFocus()

    def resetButton(self, button):
        if self.buttonBox.buttonRole(button) == QDialogButtonBox.ButtonRole.ResetRole:
            self.routeList.clear()

    def checkValid(self):
        self.okButton.setEnabled(self.uValidator.valid and len(self.shipTransponderEdit.text())==9)

    def showEvent(self, event): # This prevents any button from being a default button
        for button in self.buttonBox.buttons():
            button.setAutoDefault(False)
            button.setDefault(False)
            match self.buttonBox.buttonRole(button):
                case QDialogButtonBox.ButtonRole.AcceptRole:
                    button.setEnabled(False)
                    self.okButton = button

    def loadData(self, shipInfo: dict):
        self.shipTransponderEdit.setText(shipInfo["Registration"] if "Registration" in shipInfo else "")
        self.shipUsernameEdit.setText(shipInfo["UserNameSubmitted"] if "UserNameSubmitted" in shipInfo else "")
        self.routeList.addItems(shipInfo["Route"] if "Route" in shipInfo else ())
        self.setItemsEditable()
        #self.routeList.connect

    def addLocations(self):
        tmpStr, valid = self.lValidator.format(self.routeAddBox.text())
        if not valid:
            raise ValueError
        self.validRoute = True
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

class FleetTracker(QWidget):
    trackedShips = {}
    shipDisplayPanels = {}

    def __init__(self, PDM: PrUnDM, parent=None): 
        print("FLTR: Initialising")
        super().__init__(parent)
        self.PDM = PDM
        cur_dir = os.path.dirname(__file__)
        uic.loadUi(cur_dir+'/ui/FleetTracker.ui', self)
        PDM.fetchUserList()
        PDM.fetchPlanetNameData() # TODO: switch to initX methods
        PDM.fetchStationData()
        self.loadShips()
        self.displayShips()
    
    def loadShips(self) -> bool:
        print("FLTR: Loading Ships")
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
        print("FLTR: Adding New Ship Entry")
        self.dialog = ShipDialog(self.PDM, self)
        self.dialog.open()
        self.dialog.accepted.connect(self.acceptShipDialog)

    def displayShips(self):
        print("FLTR: Displaying Ships")
        for transponder in self.trackedShips:
            self.displayShip(transponder)

    def displayShip(self, transponder):
        shipData = self.buildShipData(transponder)
        self.shipDisplayPanels[transponder] = ShipPanel(shipData,self.PDM, self)
        self.FleetWidget.layout().addWidget(self.shipDisplayPanels[transponder])

    def buildShipData(self, transponder):
        shipData = self.PDM.getShipData(transponder)
        if not shipData:
            shipData = {
                    "Registration": transponder,
                    "UserNameSubmitted": self.trackedShips[transponder]["Username"],
                }
        shipData["Route"] = (self.trackedShips[transponder]["Route"] or []) if "Route" in self.trackedShips[transponder] else []
        return shipData
    
    def acceptShipDialog(self):
        print("FLTR: New Ship Data Valid. Adding Ship.")
        transponder = self.dialog.shipTransponderEdit.text().upper()
        success = self.createShipEntry(self.dialog)
        if not success: return success
        self.displayShip(transponder)
        return True


    def createShipEntry(self, dialog, overwrite=False) -> bool:
        items = dialog.getRouteListItems()
        routeItems = []
        for item in items:
            routeItems.append(item.text())
        transponder = dialog.shipTransponderEdit.text().upper()
        username = dialog.shipUsernameEdit.text()
        if not overwrite and transponder in self.trackedShips:
            print("FLTR: Ship registration already in memory! Delete entry first")
            return False
        self.trackedShips[transponder] = {
            "Username": username,
            "Route": routeItems,
            "PSMTracked": True,
        }
        ships = self.PDM.getAppData("ships")
        ships.update(self.trackedShips)
        self.PDM.createAppData("ships")
        self.PDM.setAppData("ships", ships)

        # TODO: Update Displayed Ships
        return True

    def closeEvent(self, event):
        print("FLTR: Closing") 
        # TODO: Move this save to the update logic instead, so that any changes are immediately reflected in the PDM. 
        # Otherwise other modules will not be able to use updated data until a close event.


class ShipPanel(QWidget):
    modified = False
    dateTimeFormat = "hh:mm   dddd"
    # TODO: Have a toggle between "Arrival Time" and "Time To Arrival"
    def __init__(self, shipInfo: dict, PDM: PrUnDM, fleetTracker: FleetTracker): 
        # Assume Transponder/Registration will always be available, as it is the primary key. 
        # In the future, I should provide a third argument for custom registrations that aren't in the ship data, cause who knows.
        super().__init__()
        self.PDM = PDM
        self.shipInfo = shipInfo
        self.registration = self.shipInfo["Registration"]
        self.fleetTracker = fleetTracker
        cur_dir = os.path.dirname(__file__)
        uic.loadUi(cur_dir+'/ui/ShipPanel.ui', self)
        self.arrivalTime = QDateTime()

        self.setNameLabel()
        self.setTransponderLabel()
        self.setDestinationLabel()
        self.setLocationLabel()
        self.setUsernameLabel()
        self.setRouteDisplay()

        self.setStorageBars()
        self.setArrivalTime()
        
        self.routeLabel.mousePressEvent = handler # THIS WORKS!!!

    def modifyEntry(self):
        print("SP: Modifying Entry of ship "+self.registration)
        self.dialog = ShipDialog(self.PDM, self)
        self.dialog.open()
        self.dialog.loadData(self.shipInfo)
        self.dialog.shipTransponderEdit.setReadOnly(True)
        self.dialog.accepted.connect(self.acceptShipDialog)
        return
    
    def acceptShipDialog(self):
        items = self.dialog.getRouteListItems()
        routeItems = []
        for item in items:
            routeItems.append(item.text())
        self.shipInfo["Route"] = routeItems
        self.setRouteDisplay()

        return self.fleetTracker.createShipEntry(self.dialog, overwrite=True)

    def setRouteDisplay(self):
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
        valid, username = self.PDM.isUser(self.shipInfo["UserNameSubmitted"] if "UserNameSubmitted" in self.shipInfo else "*Username Unavailable*")
        #userData = self.PDM.getUserInfo()
        #username = userData["UserName"] if "UserName" in userData else "*Username Unavailable*"
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
        self.fleetTracker.trackedShips[self.registration]["PSMTracked"] = False
        del self.fleetTracker.shipDisplayPanels[self.registration]
        self.deleteLater()
        print("Not Implemented!")

    def showTime(self): # Unused
            time = QDateTime.currentDateTime()
            self.arrivalTime.setDateTime(time)

