from PyQt6.QtWidgets import (QGridLayout, QWidget, QLabel)
from db_operations import (get_ventilation_system_per_building, 
                           get_total_air_supply_volume_system, 
                           get_total_air_extract_volume_system)
from PyQt6.QtGui import QFont, QColor

class SystemSettings(QWidget):
    def __init__ (self):
        super().__init__()
        self.setWindowTitle(f"Instillinger for prosjektets systemer")
        self.setGeometry(200,200,600,600)
        self.layout = QGridLayout()
        
        # Set layout and show window
        self.setLayout(self.layout)