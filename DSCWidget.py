from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtGui import QGuiApplication, QIntValidator
from PyQt6.QtWidgets import QSizePolicy

from mDisplay.MaterialDisplay import MaterialDisplay

import os

COLUMNS = 2

class DSCWidget(QWidget):
    materialData = list()
    ratioWidget = None

    def __init__(self,PDM, parent = None):
        super().__init__(parent)
        self.PDM = PDM
        cur_dir = os.path.dirname(__file__)
        uic.loadUi(cur_dir+'/ui/DiscreteShipmentCalculator.ui', self)
        self.DSCTonEntry.setValidator(QIntValidator(0,99999))
        self.DSCVolEntry.setValidator(QIntValidator(0,99999))
        self.matDisplay = MaterialDisplay(COLUMNS)
        self.matDisplay.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        self.layout().insertWidget(2,self.matDisplay)
    
    def updateMaterialList(self):
        self.matDisplay.clearRows()
        self.matDisplay.addPresetRows(self.materialData)

    def serializeMaterialData(self,materialData):
        serializedData = ""
        for materialEntry in materialData:
            serializedData += "SHIP-"+materialEntry[1]+"-"+materialEntry[0]+" "
        return serializedData


    def exportToClipboard(self):
        exportString = self.serializeMaterialData(self.materialData)
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(exportString)
        return
    
    def serialLoad(self):
        encodedString = str(self.DSCImportShipmentLine.text())
        #NOTE: Final Format will be: [CLEAR] SHIP-100-H2O-ICA-50-HRT-PROMITOR-3
        #Current Format is: [CLEAR] SHIP-100-H2O
        serialData = encodedString.strip().split(" ")

        clear = False
        valid = True
        tempData = list()
        for input in serialData:
            if input == "CLEAR":
                clear = True
            else:
                data = tuple(input.split("-"))
                if not len(data) == 3: valid = False; break
                if not (data[0]=="SHIP" and str.isnumeric(data[1]) and self.PDM.validMaterialTicker(data[2])): valid = False; break
                tempData.append((data[2],data[1]))

        if not valid:
            #TODO Signal to the user that the string is invalid?
            print("Invalid")
            return
        
        if clear:
            print("Clear")
            self.materialData.clear()

        print("Valid")
        self.materialData.extend(tempData)
        self.updateMaterialList()
        return

    def sumWeightAndVolume(self):
        weight, volume = 0, 0
        for materialEntry in self.materialData:
            tempWeight, tempVolume = self.PDM.getMaterialStorageProperties(materialEntry[0])
            weight += tempWeight*int(materialEntry[1])
            volume += tempVolume*int(materialEntry[1])
        return weight, volume

    def getShipmentConstraints(self):
        wConstraint, vConstraint = self.DSCTonEntry.text(), self.DSCVolEntry.text()

        wConstraint = int(wConstraint) if wConstraint.isnumeric() else 99999
        vConstraint = int(vConstraint) if vConstraint.isnumeric() else 99999

        return wConstraint,vConstraint
    
    def ratioMaterials(self):
        # Add all the material volumes and tonnages together. Divide available tonnage by total tonnage (ex. 300/400 = 0.75). Repeat for Volume. Get smaller of two numbers. Multiply all quantities by this number. Export.
        weight, volume = self.sumWeightAndVolume()
        if weight == 0 or volume == 0:
            return self.materialData
        wConstraint, vConstraint = self.getShipmentConstraints()
        wConstraint, vConstraint = min(wConstraint,weight), min(vConstraint,volume)
        factor = min(wConstraint/weight,vConstraint/volume)
        processedMaterialData = list()
        for materialEntry in self.materialData:
            processedMaterialData.append(list(materialEntry))
            processedMaterialData[-1][1] = str(int(factor*int(processedMaterialData[-1][1])))
        return processedMaterialData

    def returnRatios(self):
        
        if self.ratioWidget != None:
            self.ratioWidget.deleteLater()
        self.ratioWidget = QWidget()
        self.ratioMatDisplay = MaterialDisplay(COLUMNS)
        self.ratioSerial = QTextEdit()
        self.ratioSerial.setReadOnly(True)

        pMD = self.ratioMaterials()
        self.ratioMatDisplay.addPresetRows(pMD)
        spMD = self.serializeMaterialData(pMD)
        self.ratioSerial.setPlainText(spMD)

        ratioLayout = QVBoxLayout(self.ratioWidget)
        ratioLayout.addWidget(self.ratioMatDisplay)
        ratioLayout.addWidget(self.ratioSerial)
        self.ratioWidget.show()
        return
