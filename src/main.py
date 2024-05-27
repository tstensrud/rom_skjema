import db_operations as db
import sys

from PyQt6.QtWidgets import (QApplication, QMainWindow, QSplitter, QGridLayout, 
                             QTabWidget, QVBoxLayout, QWidget, QLabel, QLineEdit,
                             QPushButton, QComboBox, QMessageBox, QCheckBox)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from summary import Summary, summary_objects
from tables import RoomTable

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Romskjema")
        
        # Initiate menu
        self.set_up_top_menu()

        # Create a QSplitter
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Create the top widget (20% of the window)
        self.top_summary = Summary()
        summary_objects.append(self.top_summary)
        self.top_widget = self.top_summary
        
        self.splitter.addWidget(self.top_widget)
        self.splitter.setStretchFactor(0, 1)  # 20% weight

        # Create the bottom widget (80% of the window)
        self.bottom_widget = QTabWidget()
        self.splitter.addWidget(self.bottom_widget)
        self.splitter.setStretchFactor(1, 4)  # 80% weight

        # Set the central widget of the main window to the splitter
        self.setCentralWidget(self.splitter)
        self.generate_tabs()

        # Keep track of open windows
        self.windows = []

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar_text = QLabel("Status bar")
        self.status_bar.addPermanentWidget(self.status_bar_text)
        '''
        label.setText() for å endre label
        statusbar.showMessage("str", tid) for temp melding i statusbar
        '''

    # Generate menu bar
    def set_up_top_menu(self):
        menu = self.menuBar()
        room_menu = menu.addMenu("Rom")
        new_room = QAction("Nytt rom", self)
        new_room.triggered.connect(self.new_room_popup)
        new_room.setShortcut("Ctrl+N")
        new_room.setStatusTip("Legg til nytt rom")
        delete_room = QAction("Fjern rom", self)
        delete_room.setShortcut("Ctrl+D")
        delete_room.setStatusTip("Slet rom")
        delete_room.triggered.connect(self.delete_room)
        room_menu.addAction(new_room)
        room_menu.addAction(delete_room)
    
    # Generate one tab for each unique building found in database
    def generate_tabs(self) -> None:
        buildings = db.get_buildings()
        for i in range(len(buildings)):
            tab = QWidget()
            layout = QVBoxLayout(tab)
            table = RoomTable(buildings[i])
            
            # Add the layout to the table and the new tab
            layout.addWidget(table.get_table())
            layout.setStretch(0,1)
            self.bottom_widget.addTab(tab, f"Bygg {buildings[i]}")
    
    # Open window for adding new room
    def new_room_popup(self):
        self.new_room_window = QWidget()
        self.new_room_window.setWindowTitle(f"Legg til nye rom")
        self.new_room_window.setGeometry(150,150,300,200)
        self.new_room_layout = QGridLayout()

        # Load room types for given specification
        self.rooms: str = []
        for room in db.load_room_types("skok"):
            self.rooms.append(room)
        
        # Button, checkbox and room type menu
        self.add_button = QPushButton("Legg til")
        self.add_button.clicked.connect(self.add_new_room)
        self.room_list = QComboBox()
        self.room_list.addItems(self.rooms)
        self.several_new_rooms_check = QCheckBox("Flere rom")

        # Labels
        self.label_room_Type = QLabel("Romtype")
        self.label_building = QLabel("Bygg")
        self.label_floor = QLabel("Etasje")
        self.label_room_number = QLabel("Romnr")
        self.label_room_name = QLabel("Romnavn")
        self.label_area = QLabel("Areal")
        self.label_people = QLabel("Antall personer")
        self.label_system = QLabel("System")
        self.labels = [self.label_building, self.label_floor, self.label_room_number, 
                       self.label_room_name, self.label_area, self.label_people, self.label_system]
        
        # Entry fields
        self.entry_building = QLineEdit()
        self.entry_building.setPlaceholderText("Bygg")
        self.entry_floor = QLineEdit()
        self.entry_floor.setPlaceholderText("Etasje")
        self.entry_room_number = QLineEdit()
        self.entry_room_number.setPlaceholderText("Romnummer")
        self.entry_room_name = QLineEdit()
        self.entry_room_name.setPlaceholderText("Romnavn")
        self.entry_area = QLineEdit()
        self.entry_area.setPlaceholderText("Areal")
        self.entry_people = QLineEdit()
        self.entry_people.setPlaceholderText("Antall personer")
        self.entry_system = QLineEdit()
        self.entry_system.setPlaceholderText("System")
        entries = [self.entry_building, self.entry_floor, self.entry_room_number, self.entry_room_name,
                   self.entry_area, self.entry_people, self.entry_system]

        # Add widgets to window
        self.new_room_layout.addWidget(self.label_room_Type, 0, 0)
        self.new_room_layout.addWidget(self.room_list, 0, 1)
        
        for i in range(len(self.labels)):
            self.new_room_layout.addWidget(self.labels[i], i+1, 0)
            self.new_room_layout.addWidget(entries[i], i+1, 1)
        self.new_room_layout.addWidget(self.add_button, len(entries) + 1, 0)
        self.new_room_layout.addWidget(self.several_new_rooms_check, len(entries) + 1, 1)

        # Set layout and show window
        self.new_room_window.setLayout(self.new_room_layout)
        self.new_room_window.show()

        # Add window to tracked windows and remove it when window is destroyed
        self.windows.append(self.new_room_window)
        self.new_room_window.destroyed.connect(lambda: self.windows.remove(self.new_room_window))
        
    # Add new room to database
    def add_new_room(self) -> None:
        room_type: str = self.room_list.currentText()

        # Check if room number already exists in building       
        
        building: str = self.check_entry_field_for_empty_string(self.entry_building, "Bygg")
        floor: str = self.check_entry_field_for_empty_string(self.entry_floor, "Etasje")
        
        room_number: str = self.check_entry_field_for_empty_string(self.entry_room_number, "Romnr")
        if db.check_if_room_number_exists(room_number, building):
            messagebox.showerror(title="Feil", message=f"Romnummer finnes allerede for bygg {building}")
            return

        room_name: str = self.check_entry_field_for_empty_string(self.entry_room_name, "Romnavn")
        
        try:
            area: float = float(self.check_entry_field_for_empty_string(self.entry_area, "Areal"))
        except ValueError:
            QMessageBox.critical(self.new_room_window, "Feil", f"Areal kan kun inne holde tall")
        try:
            people: float = float(self.check_entry_field_for_empty_string(self.entry_people, "Antall personer"))
        except ValueError:
            QMessageBox.critical(self.new_room_window, "Feil", f"Antall personer kan kun inne holde tall")
        
        system: str = self.check_entry_field_for_empty_string(self.entry_system, "System")
        multiple = self.several_new_rooms_check.isChecked()

    # Delete room
    def delete_room(self):
        pass

    # Check if entry fields are empty when creating new room
    # Return content of entry field if not empty
    def check_entry_field_for_empty_string(self, entry_field, field_name) -> str:
        if entry_field.text() == "":
            QMessageBox.critical(self.new_room_window, "Feil", f"{field_name} er tomt.")
            return
        else:
            return entry_field.text().strip()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(2300, 1200)
    window.show()
    sys.exit(app.exec())
