import db_operations as db
import sys

from PyQt6.QtWidgets import (QApplication, QMainWindow, QSplitter, QGridLayout, 
                             QTabWidget, QVBoxLayout, QWidget, QLabel, QLineEdit,
                             QPushButton, QComboBox, QMessageBox, QCheckBox, QTableWidget)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from gui_windows import building_settings, system_settings
from rooms import create_new_room
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
        self.top_widget = QWidget()
        self.top_widget_layout = QVBoxLayout()
        self.top_widget.setLayout(self.top_widget_layout)
        
        self.splitter.addWidget(self.top_widget)
        self.splitter.setStretchFactor(0, 1)  # 20% weight

        # Create the bottom widget (80% of the window)
        self.bottom_widget = QTabWidget()
        self.splitter.addWidget(self.bottom_widget)
        self.splitter.setStretchFactor(1, 4)  # 80% weight
        self.bottom_widget.currentChanged.connect(self.tab_change)
        
        # Set up dictionary for tables for each building
        self.tables = {}
        self.current_summary = None

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
        room_menu.addAction(new_room)

        project_menu = menu.addMenu("Prosjektinnstillinger")
        bygg = QAction("Bygg", self)
        bygg.triggered.connect(self.building_settings_window)
        bygg.setStatusTip("Innstillinger for prosjektets bygg")
        systems = QAction("Systemer", self)
        systems.triggered.connect(self.system_settings_window)
        systems.setStatusTip("Innstillinger for systemer")
        project_menu.addAction(bygg)
        project_menu.addAction(systems)

    
    # Generate one tab for each table found in database
    def generate_tabs(self) -> None:
        buildings = db.get_all_tables()
        for i in range(len(buildings)):
            tab = QWidget()
            layout = QVBoxLayout(tab)
            table = RoomTable(buildings[i])
            self.tables[buildings[i]] = table

            # Get the table-summary object and hide it before adding to top_widget_layout
            table_summary = table.get_summary_object()
            table_summary.hide()
            self.top_widget_layout.addWidget(table_summary)

            # Add the layout to the table and the new tab
            layout.addWidget(table.get_table())
            layout.setStretch(0,1)
            self.bottom_widget.addTab(tab, f"Bygg {buildings[i]}")

    # Update summary depending on what tab is clicked
    def tab_change(self, index):
        table = self.bottom_widget.widget(index).findChild(QTableWidget)
        if self.current_summary is not None:
            self.current_summary.hide()
        self.current_summary = table.get_summary_object()
        self.current_summary.show()

    # Window for managing and summarizing buildings in project
    def building_settings_window(self):
        window = building_settings.BuildingSettings()
        window.show()
        
        # Add window to tracked windows and remove it when window is destroyed
        self.windows.append(window)
        #window.destroyed.connect(lambda: self.building_settings_window_closed(window))
        window.window_closed.connect(lambda: self.building_settings_window_closed(window))

    def building_settings_window_closed(self, window):
        self.windows.remove(window)


    # Window for managing and summarizing systems in project
    def system_settings_window(self):
        window = system_settings.SystemSettings()
        window.show()

        # Add window to tracked windows and remove it when window is destroyed
        self.windows.append(window)
        window.destroyed.connect(lambda: self.windows.remove(window))
    
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
        buildings = db.get_all_tables()
        self.building_list_cbox = QComboBox()
        self.building_list_cbox.addItems(buildings)

        self.room_list_qbox = QComboBox()
        self.room_list_qbox.addItems(self.rooms)

        self.add_button = QPushButton("Legg til")
        self.add_button.clicked.connect(self.add_new_room)
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
        entries = [self.building_list_cbox, self.entry_floor, self.entry_room_number, self.entry_room_name,
                   self.entry_area, self.entry_people, self.entry_system]

        # Add widgets to window
        self.new_room_layout.addWidget(self.label_room_Type, 0, 0)
        self.new_room_layout.addWidget(self.room_list_qbox, 0, 1)
        
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
        room_type: str = self.room_list_qbox.currentText()
        
        building: str = self.check_entry_field_for_empty_string(self.building_list_cbox, "Bygg")
        floor: str = self.check_entry_field_for_empty_string(self.entry_floor, "Etasje").strip()
        
        room_number: str = self.check_entry_field_for_empty_string(self.entry_room_number, "Romnr").strip()
        if db.check_if_room_number_exists(room_number, building):
            QMessageBox.critical(self.new_room_window, "Feil", f"Romnummer finnes allerede for bygg {building}")
            return

        room_name: str = self.check_entry_field_for_empty_string(self.entry_room_name, "Romnavn").strip()
        
        try:
            area: float = float(self.check_entry_field_for_empty_string(self.entry_area, "Areal").strip())
        except ValueError:
            QMessageBox.critical(self.new_room_window, "Feil", f"Areal kan kun inne holde tall")
        try:
            people: float = float(self.check_entry_field_for_empty_string(self.entry_people, "Antall personer").strip())
        except ValueError:
            QMessageBox.critical(self.new_room_window, "Feil", f"Antall personer kan kun inne holde tall")
        
        system: str = self.check_entry_field_for_empty_string(self.entry_system, "System").strip()
        if self.several_new_rooms_check.isChecked():
            self.entry_room_number.clear()
            self.entry_room_name.clear()
            self.entry_area.clear()
            self.entry_people.clear()
        else:
            self.new_room_window.close()
            self.windows.clear()
        
        # Add new room to database
        new_room_id = create_new_room("skok", building, room_type, floor, room_number, room_name, people, area, system)

        # Update table for building of new room
        table = self.tables[building]
        table.add_new_room(new_room_id)

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
