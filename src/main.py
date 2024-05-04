import sys
from rooms import *
from PyQt6.QtWidgets import(QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout,
                            QToolBar, QMessageBox, QPushButton)
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


        self.menu_bar = self.menuBar()

        self.file_menu = self.menu_bar.addMenu('&Fil')
        self.edit_menu = self.menu_bar.addMenu('&Rom')
        self.help_menu = self.menu_bar.addMenu('&Hjelp')

        # new menu item
        self.new_action = QAction('&Nytt rom', self)
        self.new_action.setStatusTip('Nytt rom')
        self.new_action.setShortcut('Ctrl+N')
        self.new_action.triggered.connect(self.new_room)
        self.file_menu.addAction(self.new_action)

        # open menu item
        self.open_action = QAction('&Fjern rom', self)
        self.open_action.triggered.connect(self.remove_room)
        self.open_action.setStatusTip('Fjern')
        self.open_action.setShortcut('Ctrl+O')
        self.file_menu.addAction(self.open_action)

        # save menu item
        self.save_action = QAction('&Lagre', self)
        self.save_action.setStatusTip('Lagre')
        self.save_action.setShortcut('Ctrl+S')
        #self.save_action.triggered.connect()
        self.file_menu.addAction(self.save_action)

        self.file_menu.addSeparator()

        # exit menu item
        self.exit_action = QAction('&Avslutt', self)
        self.exit_action.setStatusTip('Avslutt')
        self.exit_action.setShortcut('Alt+F4')
        #self.exit_action.triggered.connect()
        self.file_menu.addAction(self.exit_action)

        # edit menu
        self.undo_action = QAction('&Angre', self)
        self.undo_action.setStatusTip('Angre')
        self.undo_action.setShortcut('Ctrl+Z')
        #self.undo_action.triggered.connect()
        self.edit_menu.addAction(self.undo_action)

        self.redo_action = QAction('&Gjenta', self)
        self.redo_action.setStatusTip('Gjenta')
        self.redo_action.setShortcut('Ctrl+Y')
        #self.redo_action.triggered.connect()
        self.edit_menu.addAction(self.redo_action)

        self.about_action = QAction( 'Om', self)
        self.help_menu.addAction(self.about_action)
        self.about_action.setStatusTip('Om')
        self.about_action.setShortcut('F1')

        # toolbar
        self.toolbar = QToolBar('Verktøy')
        self.addToolBar(self.toolbar)
        self.toolbar.setIconSize(QSize(16, 16))

        self.toolbar.addAction(self.new_action)
        self.toolbar.addAction(self.open_action)
        self.toolbar.addSeparator()

        self.toolbar.addAction(self.undo_action)
        self.toolbar.addAction(self.redo_action)
        self.toolbar.addSeparator()

        # status bar
        self.status_bar = self.statusBar()
        self.show()




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

    def remove_room(self, row_number: int) -> None:
        message = QMessageBox.question(self, "Confirmation", "Fjerne rad?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if message == QMessageBox.StandardButton.Yes:
            print("removed")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())