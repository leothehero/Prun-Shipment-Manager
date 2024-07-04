from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtGui import QGuiApplication, QIntValidator
from PyQt6.QtWidgets import QSizePolicy

import os

class FleetTracker(QWidget):
    trackedShips = {}

    def __init__(self,PDM):
        super().__init__()
        self.PDM = PDM
        cur_dir = os.path.dirname(__file__)
        uic.loadUi(cur_dir+'/ui/FleetTracker.ui', self)
        self.loadShips()
    
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
            if "username" in self.trackedShips[transponder]:
                usernames.push(self.trackedShips[transponder]["username"])
        self.PDM.fetchFleetsByUsers(usernames)
    
    def configureToggle(self,state):
        print(("Entering" if state else "Exiting")+" Fleet Configuration Mode")