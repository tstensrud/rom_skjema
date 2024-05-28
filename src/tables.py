from PyQt6.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QMenu, 
                             QMessageBox, QGridLayout, QLabel)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction

from rooms import get_room_sql_data_to_json
from db_operations import *
from summary import BuildingSummary

class RoomTable(QTableWidget):
    def __init__ (self, building):
        self.building = building

        # These columns should not be editable
        self.locked_columns =  [0,7,8,9,10,12,15,16,17,18]

        # Define column headers
        self.columns=["rom-id", "Bygg", "Etasje", "Romnr", "Romnavn", "Areal", "Antall_pers", "Luft per pers", 
                    "Sum personer", "Emisjon", "Sum emisjon", "Prosess", "Dimensjonert", 
                    "Tilluft", "Avtrekk", "Valgt", "Gjenvinner", "Prinsipp", "Styring", "System"]
        
        # Query databse for all rooms for this building
        self.rooms = get_all_rooms(building)
        
        # Set # of columns and rows upon initiating the table
        super().__init__(len(self.rooms), len(self.columns))
        
        # Insert data from database
        self.insert_data_from_db()
        
        # Set table view settings
        for i in range(3):
            self.resizeColumnToContents(i)
        self.setColumnWidth(4, 250)
        self.setHorizontalHeaderLabels(self.columns)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # Listeners for interaction with table
        self.itemChanged.connect(self.changed_cell) # for changed cell value
        self.cell_updating = False
        self.horizontalHeader().sectionClicked.connect(self.sort_rows) # for click on header

        # Custom context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.table_right_click_menu)    
        
        # Keep track of opened windows
        self.opened_windows = []

        self.building_summary = BuildingSummary(self.building)

    # Right-click menu bar on table
    def table_right_click_menu(self, position: QPoint):
        table_right_click_menu = QMenu()
        table_right_click_menu_summary_room_action = QAction("All rom-data", self)
        table_right_click_menu_delete_room_action = QAction("Slett rom", self)
        table_right_click_menu.addAction(table_right_click_menu_summary_room_action)
        table_right_click_menu.addAction(table_right_click_menu_delete_room_action)
        
        # Detect clicked row and get it's row and room-index
        row = self.verticalHeader().logicalIndexAt(position)
        room_id = self.item(row,0).text()
        action = table_right_click_menu.exec(self.mapToGlobal(position))
        
        # Action if delete room is clicked
        if action == table_right_click_menu_delete_room_action:
            delete_room(room_id)
            self.removeRow(row)
        if action == table_right_click_menu_summary_room_action:
            self.get_room_summary(room_id)
    
    # Change double click listener to ensure locked cells are uneditable
    def mouseDoubleClickEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid() and index.column() in self.locked_columns:
            return
        super().mouseDoubleClickEvent(event)
    
    # Insert data from database when program loads
    def insert_data_from_db(self) -> None:
        for row, row_data in enumerate(self.rooms):
            for col, value in enumerate(row_data):               
                self.setItem(row, col, QTableWidgetItem(str(value)))

    # Insert new row at the end of table or at given index.
    # Can also be used to update existing row.
    def update_table_row(self, updated_row, row_insertion: int, end: bool) -> None:
        row_index = row_insertion
        if end == True:
            row_index = self.rowCount()
        self.insertRow(row_index)
        for column, data in enumerate(updated_row):
            self.setItem(row_index, column, QTableWidgetItem(str(data)))
        
        # update summary at top of mainwindow
        #summary_objects[0].intiate_labels()
    
    def add_new_room_to_table(self, room_id):
        if self.cell_updating == True:
            return
        self.cell_updating = True
        try:
            self.itemChanged.disconnect(self.changed_cell) 
            new_room_data = get_room_table_data(room_id)
            last_row = self.rowCount()
            self.insertRow(last_row)
            for column, data in enumerate(new_room_data):
                self.setItem(last_row, column, QTableWidgetItem(str(data)))
            self.sort_rows(2)
        finally:
            self.itemChanged.connect(self.changed_cell)
            self.cell_updating = False

    # Handle the change of value in a cell
    def changed_cell(self, item) -> str:
        if self.cell_updating == True:
            return
        
        row = item.row() # get current row
        column = str(item.column()) # get text of column header
        room_id = self.item(row,0).text() # get row index 0 which is room id
        new_value = item.text()
        
        self.cell_updating = True
        try:
            # disconnect to ensure cell does not try to update twice
            self.itemChanged.disconnect(self.changed_cell) 
            # send new value to update database
            if update_db_table_value(room_id, column, new_value):
                # get updated room data from database after update
                updated_row = get_room_table_data(room_id)

                # close cell-editor and remove the old row
                self.closePersistentEditor(self.currentItem())
                self.removeRow(row)
                
                # Insert update row into table and sort table
                self.update_table_row(updated_row, row, False)
                #self.sortItems(2) # sort by floor first
                
            else:
                QMessageBox.critical(self, "Feil", f"Kunne ikke oppdatere data")
        finally:
            # Rreconnect and reopen cell for option to change
            self.itemChanged.connect(self.changed_cell)
            self.cell_updating = False
    
    # Sort rows when one of the headers are clicked
    def sort_rows(self, section):
        sortable_columns = [2,3,4,19]
        if section in sortable_columns:
            self.sortItems(section, Qt.SortOrder.AscendingOrder)

    # Get complete room summary
    def get_room_summary(self, room_id):
        # Get room data and deserialize
        room_data = get_room_sql_data_to_json(room_id)
        room_data_deserialized = json.loads(room_data)
        items = room_data_deserialized[0]
        
        summary_window = QWidget()
        summary_window.setWindowTitle(f"Rom-data")
        summary_window.setGeometry(150,150,300,200)
        layout = QGridLayout()

        # Place key and value in a grid layout
        for i, (key, value) in enumerate(items.items(), start=1):
            label_key = QLabel(f"{key}")
            label_value = QLabel(f"{value}")    
            layout.addWidget(label_key, i, 0)
            layout.addWidget(label_value, i, 1)

        # Set layout and show window
        summary_window.setLayout(layout)
        summary_window.show()

        # Add window to tracked windows and remove it when window is destroyed
        self.opened_windows.append(summary_window)
        summary_window.destroyed.connect(lambda: self.opened_windows.remove(summary_window))
    
    def get_summary_object(self):
        return self.building_summary
    
    def get_building(self) -> str:
        return self.building
    
    def get_table(self):
        return self