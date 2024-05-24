import tkinter as tk
import db_operations as db
import json
import sys

from PyQt6.QtWidgets import (QApplication, QMainWindow, QSplitter, QTextEdit, QGridLayout, 
                             QTabWidget, QVBoxLayout, QWidget, QLabel)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from tkinter import messagebox

from tables import RoomTable
from rooms import get_room_sql_data_to_json, create_new_room


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
        self.top_widget_layout = QGridLayout()
        self.top_widget.setLayout(self.top_widget_layout)
        self.splitter.addWidget(self.top_widget)
        self.splitter.setStretchFactor(0, 1)  # 20% weight

        # Initate top widget widgets
        self.set_up_top_summary()

        # Create the bottom widget (80% of the window) with QTabWidget
        self.bottom_widget = QTabWidget()
        self.splitter.addWidget(self.bottom_widget)
        self.splitter.setStretchFactor(1, 4)  # 80% weight

        # Set the central widget of the main window to the splitter
        self.setCentralWidget(self.splitter)
        self.generate_tab()

    # Generate summary for top part of window
    def set_up_top_summary(self):
        systems = db.get_ventilation_systems()
        systems.sort()
        for i in range(len(systems)):
            system_name = QLabel(systems[i])
            system_airflow_supply = f"Tilluft: {db.get_total_air_supply_volume_system(systems[i])} m3/h"
            system_airflow_extract = f"Avtrekk: {db.get_total_air_extract_volume_system(systems[i])} m3/h"
            system_airflow_supply_label = QLabel(system_airflow_supply)
            system_airflow_extract_label = QLabel(system_airflow_extract)
            self.top_widget_layout.addWidget(system_name, 0, i)
            self.top_widget_layout.addWidget(system_airflow_supply_label, 1, i)
            self.top_widget_layout.addWidget(system_airflow_extract_label, 2, i)

    # Generate menu bar
    def set_up_top_menu(self):
        menu = self.menuBar()
        room_menu = menu.addMenu("Rom")
        new_room = QAction("Nytt rom", self)
        # new_room.triggered.connect(self.new_room_popup)
        delete_room = QAction("Fjern rom", self)
        # delete_room.triggered.connect(self.remove_room)

        room_menu.addAction(new_room)
        room_menu.addAction(delete_room)

    # Generate one tab for each unique building found in database
    def generate_tab(self) -> None:
        buildings = db.get_buildings()
        for i in range(len(buildings)):
            tab = QWidget()
            layout = QVBoxLayout(tab)
            table = RoomTable(buildings[i])
            
            # Add the layout to the table and the new tab
            layout.addWidget(table.get_table())
            layout.setStretch(0,1)
            self.bottom_widget.addTab(tab, f"Bygg {buildings[i]}")
        
    
    # Project summary placed on top of main window
    def update_top_frame_summary(self):
        systems = db.get_ventilation_systems()
        systems.sort()
        # clear all widgest
        for widget in self.top_frame.winfo_children():
            widget.destroy()
        # draw updated list of widgets
        for i in range(len(systems)):
            label_system = tk.Label(self.top_frame, text=f"{systems[i]}")
            label_volume = tk.Label(self.top_frame, text=f"{db.get_total_air_supply_volume_system(systems[i])} m3/h")
            label_system.grid(column=i, row=0, padx=10, pady=5)
            label_volume.grid(column=i, row=1, padx=10, pady=2)

    
    # Open window for adding new room
    def new_room_popup(self):
        pass
     
    
    # Room description that lists all data for specified room
    # Shown in own window
    def room_description(self):
        event = self.saved_event
        region = self.room_table.identify("region", event.x, event.y)
        if region != "cell":
            return
        row = self.room_table.identify_row(event.y)
        row_values = self.room_table.item(row, "values")
        room_id = row_values[0]
        room_data = get_room_sql_data_to_json(room_id)
        room_data_deserialized = json.loads(room_data)
        items = room_data_deserialized[0]
        description_window = tk.Toplevel(self.root)
        description_window.title("Beskrivelse")
        description_window.geometry("400x900")

        for i, (key, value) in enumerate(items.items(), start=1):
            label_key = tk.Label(description_window, text=f"{key}:")
            label_value = tk.Label(description_window, text=f" {value}")
            label_key.grid(column=0, row=i, padx=5, pady=3, sticky="w")
            label_value.grid(column=1, row=i, padx=5, pady=3, sticky="w")
    

    # Aadd new room to database
    def add_new_room(self) -> None:
        multiple = self.new_room_check_state.get()
        building: str = self.new_room_building_entry.get().strip()
        room_type: str = self.new_room_combobox.get().strip()
        floor: str = self.new_room_floor_entry.get().strip()
        room_number: str = self.new_room_roomnr_entry.get().strip()
        if db.check_if_room_number_exists(room_number, building):
            messagebox.showerror(title="Feil", message=f"Romnummer finnes allerede for bygg {building}")
            return
        name: str = self.new_room_roomname_entry.get().strip()
        
        try:
            population: int = int(self.new_room_people_entry.get().strip())
        except ValueError:
            messagebox.showerror(title="Feil", message="Kun tall i antall personer")
            return
        
        try:
            area: float = float(self.new_room_area_entry.get().strip())
        except ValueError:
            messagebox.showerror(title="Feil", message="Kun tall i areal")
            return
        
        system: str = self.new_room_system_entry.get().strip()
        
        if room_type == "Romtype":
            messagebox.showerror(title="Feil", message="Velg romtype")
            return
        create_new_room("skok", building, room_type, floor, room_number, name, population, area, system)
        self.update_room_list(None)
        

        if multiple == 0:
            self.update_top_frame_summary()
            self.new_room_window.destroy()
        else:
            self.update_top_frame_summary()
            self.new_room_roomnr_entry.delete(0, tk.END)
            self.new_room_roomname_entry.delete(0, tk.END)
            self.new_room_people_entry.delete(0, tk.END)
            self.new_room_area_entry.delete(0, tk.END)
   
    # Remove room from project
    def remove_room(self) -> None:       
        if messagebox.askokcancel(title="Fjern rom", message="Vil du fjerne rom?"):
            for selected_item in self.room_table.selection():
                row_values = self.room_table.item(selected_item, 'values')
                room_number = row_values[3]
                db.delete_room(room_number)
                self.room_table.delete(selected_item)
                self.update_top_frame_summary()
                self.update_room_list(None)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(2300, 1200)
    window.show()
    sys.exit(app.exec())
        
        