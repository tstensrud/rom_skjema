import sys
from rooms import Room, RoomRow
from PyQt6.QtWidgets import(QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout,
                            QToolBar, QMessageBox, QPushButton)
from PyQt6.QtCore import Qt,QSize
from PyQt6.QtGui import QIcon, QAction

# sqlite


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rooms = []

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
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(self.table_headers)
        self.table.verticalHeader().setMinimumWidth(50)
        self.setCentralWidget(self.table)


        self.menu_bar = self.menuBar()

        self.file_menu = self.menu_bar.addMenu('&Fil')
        self.edit_menu = self.menu_bar.addMenu('&Rom')
        self.help_menu = self.menu_bar.addMenu('&Hjelp')

        # new menu item
        self.new_action = QAction('&Nytt rom', self)
        self.new_action.setStatusTip('Nytt rom')
        self.new_action.setShortcut('Ctrl+N')
        #self.new_action.triggered.connect(self.new_room)
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
        self.undo_action = QAction('&Slett', self)
        self.undo_action.setStatusTip('Slett')
        self.undo_action.setShortcut('Del')
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

        # TEST ROOMs
        self.new_room("undervisningsrom","1", "A-12354", "Klasserom", 35, 150, "360.001")
        self.new_room("grupperom","1", "A-13254", "Grupperom", 35, 150, "360.001")
        self.new_room("vestibyle","1", "A-13333", "Vestibyle", 100, 250, "360.001")
        self.new_room("korridor","1", "A-9999", "korridor", 10, 100, "360.001")
        self.new_room("bibliotek","1", "A-13232", "bibliotek", 50, 500, "360.001")

    def new_room(self, type, floor, room_number, name, population, area, system):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        new_room = Room(type, floor, room_number, name, population, area, system)
        self.rooms.append(new_room)

        new_room_row = RoomRow(new_room, row)
        
        
        button = QPushButton("Fjern")
        button.clicked.connect(lambda: self.remove_room(row))
        
        for i in range(len(new_room_row.columns)):
            self.table.setItem(row, i, new_room_row.columns[i])
    
    # get room-index based on room_number from self.rooms-list
    def find_room(self, room_number):
        for i in range(len(self.rooms)):
            if self.rooms[i].get_room_number() == room_number:
                return i
    
        
    def remove_room(self) -> None:
        message = QMessageBox.question(self, "Confirmation", "Fjerne rad?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        current_row = self.table.currentRow()
        if message == QMessageBox.StandardButton.Yes:
            room_number = self.table.item(current_row, 1).text()
            self.rooms.pop(self.find_room(room_number))
            self.table.removeRow(current_row)
            


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
        
        