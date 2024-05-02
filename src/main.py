import sys
from rooms import *
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QToolBar
from PyQt6.QtCore import Qt,QSize
from PyQt6.QtGui import QIcon, QAction

# sqlite

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        self.setWindowTitle("Romskjema")
        self.setGeometry(100, 100, 2048, 1024)
        self.table_headers = ["Etasje", "Romnr", "Romnavn", "Areal", "Personer", "Luft per person",
                              "Summert personbelastning", "Emisjon / m2", "Summert emisjon",
                              "Prosess", "Dimensjonert", "Tilluft", "Avtrekk",
                              "Valgt", "Gjenvinner", "Ventilasjonsprinsipp", "Styring", "System"]
        self.table = QTableWidget(self)
        self.table.setColumnCount(len(self.table_headers))
        self.table.setHorizontalHeaderLabels(self.table_headers)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().resizeSection(1, 100) # width of room-number cell
        self.table.horizontalHeader().resizeSection(2, 150)
        self.table.horizontalHeader().resizeSection(3, 75)
        self.table.horizontalHeader().resizeSection(9, 100)
        self.table.horizontalHeader().resizeSection(11, 100)
        self.table.horizontalHeader().resizeSection(12, 100)
        self.table.horizontalHeader().resizeSection(13, 150)
        self.table.horizontalHeader().resizeSection(16, 100)
        self.table.horizontalHeader().resizeSection(len(self.table_headers)-1, 150)
        self.table.setRowCount(1)
        self.table.setHorizontalHeaderLabels(self.table_headers)
        self.setCentralWidget(self.table)

        # TOOLBAR
        self.toolbar = QToolBar("toolbar")
        self.toolbar.setIconSize(QSize(16,16))
        self.addToolBar(self.toolbar)
        self.new_room_button = QAction("Nytt rom", self)
        self.new_room_button.triggered.connect(self.new_room)
        self.toolbar.addAction(self.new_room_button)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def new_room(self):
        new_room = Room("undervisningsrom","1", "A-12354", "Klasserom", 35, 150, "360.001")
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(new_room.floor))
        self.table.setItem(row, 1, QTableWidgetItem(new_room.room_number))
        self.table.setItem(row, 2, QTableWidgetItem(new_room.room_name))
        self.table.setItem(row, 3, QTableWidgetItem(f"{new_room.area} m2"))
        self.table.setItem(row, 4, QTableWidgetItem(f"{new_room.room_population} stk"))
        self.table.setItem(row, 5, QTableWidgetItem(f"{new_room.air_per_person} m3/h"))
        self.table.setItem(row, 6, QTableWidgetItem(f"{new_room.get_ventilation_sum_persons()} m3/h"))
        self.table.setItem(row, 7, QTableWidgetItem(f"{new_room.air_emission} m3/h"))
        self.table.setItem(row, 8, QTableWidgetItem(f"{new_room.get_sum_emission()} m3/h"))
        self.table.setItem(row, 9, QTableWidgetItem(f"{new_room.air_process} m3/h"))
        self.table.setItem(row, 10, QTableWidgetItem(f"{new_room.get_required_air()} m3/h"))
        self.table.setItem(row, 11, QTableWidgetItem(f"{new_room.chosen_air_supply} m3/h"))
        self.table.setItem(row, 12, QTableWidgetItem(f"{new_room.chosen_air_exhaust} m3/h"))
        self.table.setItem(row, 13, QTableWidgetItem(f"{new_room.get_air_per_area()} m3/m2"))
        self.table.setItem(row, 14, QTableWidgetItem(f"{new_room.heat_exchange}"))
        self.table.setItem(row, 15, QTableWidgetItem(new_room.get_ventilation_principle()))
        self.table.setItem(row, 16, QTableWidgetItem(new_room.get_room_controls()))
        self.table.setItem(row, 17, QTableWidgetItem(new_room.system))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())