import sys
from rooms import *
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget,
    QTableWidgetItem, QDockWidget, QFormLayout,
    QLineEdit, QWidget, QPushButton, QSpinBox,
    QMessageBox, QToolBar, QMessageBox
)
from PyQt6.QtCore import Qt,QSize
from PyQt6.QtGui import QIcon, QAction

# sqlite

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        self.setWindowTitle("Romskjema")
        self.setGeometry(100,100,1024,768)


        self.table_headers = ["Romnr", "Romnavn", "Romtype", "Areal", "Personer"]
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        
        self.table.setRowCount(2)
        self.table.setHorizontalHeaderLabels(self.table_headers)



        #label_luft = QLabel(f"Dimensjonert luftmengde: {new_room.get_room().get_required_air()}")
        #label_req = QLabel(f"Minste luftmengde: {new_room.get_room().get_minium_air()}")
        self.layout = QFormLayout()
        self.setLayout(self.layout)

    #new_room = RoomUndervisningsAreal("A-12354", "klasserom", 107, 35)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())