from PyQt6.QtWidgets import (QGridLayout, QWidget, QLabel, QLineEdit, QPushButton, 
                             QMessageBox, QComboBox)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import pyqtSignal

from gui_windows.messageboxes import *
from db_operations import create_room_table, delete_table, get_all_tables

class BuildingSettings(QWidget):
    window_closed = pyqtSignal(QWidget)
    def __init__ (self):
        super().__init__()
        self.setWindowTitle(f"Instillinger for prosjektets bygg")
        self.setGeometry(200,200,600,600)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.add_building_widgets()
        self.remove_building_widgets()
        
        self.button = QPushButton("Lagre", self)
        self.layout.addWidget(self.button, 2,0)
        self.button.clicked.connect(self.close)

    def add_building_widgets(self):
        self.new_building_label = QLabel("Nytt bygg")
        self.new_building_entry = QLineEdit()
        self.new_building_button = QPushButton("Legg til")
        self.new_building_button.clicked.connect(self.add_building)
        self.new_building_entry.setPlaceholderText("Byggningsnavn eller nr. Eks \"A\", \"Mellombygg\"")
        self.layout.addWidget(self.new_building_label, 0, 0)
        self.layout.addWidget(self.new_building_entry, 0, 1)
        self.layout.addWidget(self.new_building_button, 0, 2)

    def add_building(self):
        building = self.new_building_entry.text().strip()
        create_room_table(building)
        information_box("Opprettet", f"Bygg {building} er opprettet.")
        self.remove_building_combo.insertItem(self.remove_building_combo.count(), building)

    def summary_widgets(self):
        pass
    
    def remove_building_widgets(self):
        buildings = get_all_tables()
        self.remove_building_label = QLabel("Slett bygg")
        self.remove_building_combo = QComboBox()
        self.remove_building_combo.addItems(buildings)

        self.remove_building_button = QPushButton("Slett")
        self.remove_building_button.clicked.connect(self.remove_building)
        self.layout.addWidget(self.remove_building_label, 1, 0)
        self.layout.addWidget(self.remove_building_combo, 1, 1)
        self.layout.addWidget(self.remove_building_button, 1, 2)

    def remove_building(self):
        box = QMessageBox()
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Slette?")
        box.setText("Er du helt sikker på at du vil slette bygg? Dette vil fjerne all data assosiert med dette bygget!")
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        box.setDefaultButton(QMessageBox.StandardButton.No)
        box_response = box.exec()
        if box_response == QMessageBox.StandardButton.Yes:
            building = self.remove_building_combo.currentText()
            delete_table(building)
            information_box("Slettet", f"Bygg {building} er slettet")
            for i in range(self.remove_building_combo.count()):
                item_text = self.remove_building_combo.itemText(i)
                if item_text == building:
                    self.remove_building_combo.removeItem(i)
                    break
        else:
            print("Ikke slettet")
    
    def closeEvent(self, event):
        self.window_closed.emit(self)
        event.accept()