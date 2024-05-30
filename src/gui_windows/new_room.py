from PyQt6.QtWidgets import (QGridLayout, QWidget, QLabel)
from PyQt6.QtGui import QFont, QColor

class NewRoom(QWidget):
    def __init__ (self):
        super().__init__()
        self.setWindowTitle(f"Legg til nye rom")
        self.setGeometry(150,150,300,200)
        self.new_room_layout = QGridLayout()
        
        # Set layout and show window
        self.setLayout(self.layout)