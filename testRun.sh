pyside6-rcc PSM/PSMresources.qrc | sed '0,/PySide6/s//PyQt6/' > PSM/PSMresources.py
python3 PSM/PSMMain.py