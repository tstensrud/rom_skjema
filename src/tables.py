from PyQt6.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QMenu, 
                             QMessageBox, QGridLayout, QLabel)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction, QColor

from rooms import get_room_sql_data_to_json
from db_operations import *
from gui_windows import messageboxes
from summary import BuildingSummary

class RoomTable(QTableWidget):
    def __init__ (self, building):
        self.building = building

        # These columns should not be editable
        self.locked_columns =  [0,1,7,8,9,10,12,15,16,17,18]

        # Define column headers
        self.columns=["rom-id", "Bygg", "Etasje", "Romnr", "Romnavn", "Areal", "Antall_pers", "Luft per pers", 
                    "Sum personer", "Emisjon", "Sum emisjon", "Prosess", "Dimensjonert", 
                    "Tilluft", "Avtrekk", "Valgt", "Gjenvinner", "Prinsipp", "Styring", "System", "Kommentar"]
        
        # Query databse for all rooms for this building
        self.rooms = get_all_rooms(building)
        
        # Set # of columns and rows upon initiating the table
        super().__init__(len(self.rooms) + 1, len(self.columns))
        
        # Insert data from database
        self.insert_data_from_db()
        
        # Set table view settings
        for i in range(3):
            self.resizeColumnToContents(i)
        self.setColumnWidth(4, 250)
        self.setHorizontalHeaderLabels(self.columns)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setSectionResizeMode(self.columnCount() - 1, QHeaderView.ResizeMode.Stretch)

        # Listeners for interaction with table
        self.itemChanged.connect(self.changed_cell) # for changed cell value
        self.cell_updating = False
        self.horizontalHeader().sectionClicked.connect(self.sort_rows) # for click on header

        # Custom context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.table_right_click_menu)    
        
        # Keep track of opened windows
        self.opened_windows = []

        # Create a building summary object to place on main window
        self.building_summary = BuildingSummary(self.building)

    def table_right_click_menu(self, position: QPoint):
        table_right_click_menu = QMenu()
        table_right_click_menu_summary_room_action = QAction("All rom-data", self)
        table_right_click_menu_delete_room_action = QAction("Slett rom", self)
        table_right_click_menu.addAction(table_right_click_menu_summary_room_action)
        table_right_click_menu.addAction(table_right_click_menu_delete_room_action)
        
        # Detect clicked row and get it's row and room-index
        row = self.verticalHeader().logicalIndexAt(position)
        try:
            room_id = self.item(row,0).text()
        except AttributeError:
            return
        action = table_right_click_menu.exec(self.mapToGlobal(position))
        
        # Actions for right-click menu
        if action == table_right_click_menu_delete_room_action:
            delete_room(self.building, room_id)
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
        self.column_summaries()
    
    # Insert column summaries for all floors
    def column_summaries(self) -> None:
        columns_for_summary = [5, 8, 10, 11, 12, 13, 14]
        for column in columns_for_summary:
            column_sum = get_sum_of_column_building_floor(self.building, None, column)
            column_input = ""
            
            if column == 5:
                column_input = f"{column_sum} m2"
            else:
                column_input = f"{column_sum} m3/h"
            table_item = QTableWidgetItem(str(column_input))
            table_item.setBackground(QColor(100,100,100))
            self.setItem(self.rowCount() - 1, column, table_item)

    # Insert new row at the end of table or at given index.
    # Can also be used to update existing row.
    def update_table_row(self, updated_row, row_insertion: int, end: bool) -> None:
        row_index = row_insertion
        if end == True:
            row_index = self.rowCount()
        self.insertRow(row_index)
        for column, data in enumerate(updated_row):
            table_item = QTableWidgetItem(str(data))
            self.setItem(row_index, column, table_item)
        
        self.update_buildnig_summary()
    
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
        column = item.column() # get column index
        room_id = self.item(row,0).text() # get row index 0 which is room id
        new_value = item.text()
        self.cell_updating = True
        
        try:
            # Disconnect to ensure cell does not try to update twice
            self.itemChanged.disconnect(self.changed_cell)
            
            # Check if new room number already exists. If it does, insert old value back into cell
            old_value = get_single_cell_value(self.building, room_id, column)
            if check_if_room_number_exists(new_value, self.building) == True:
                messageboxes.information_box("Feil romnr", f"Romnummer {new_value} finnes allerede i bygg {self.building}")
                self.item(row,column).setText(old_value)
                return
            
            # Send new value to update database
            if update_db_table_value(self.building, room_id, column, new_value):

                # get updated room data from database after update
                updated_row = get_room_table_data(self.building, room_id)

                # close cell-editor and remove the old row
                self.closePersistentEditor(self.currentItem())
                self.removeRow(row)
                
                # Insert update row into table and sort table
                self.update_table_row(updated_row, row, False)
                
            else:
                QMessageBox.critical(self, "Feil", f"Kunne ikke oppdatere data. Finnes romnr allerede?")
        finally:
            # Rreconnect and reopen cell for option to change
            self.itemChanged.connect(self.changed_cell)
            self.cell_updating = False
    
    def sort_rows(self, section):
        sortable_columns = [2,3,4,19]
        if section in sortable_columns:
            self.sortItems(section, Qt.SortOrder.AscendingOrder)

    # Get complete room summary
    def get_room_summary(self, room_id):
        
        room_data = get_room_sql_data_to_json(room_id)
        room_data_deserialized = json.loads(room_data)
        items = room_data_deserialized[0]
        
        summary_window = QWidget()
        summary_window.setWindowTitle(f"Rom-data")
        summary_window.setGeometry(150,150,300,200)
        layout = QGridLayout()

        for i, (key, value) in enumerate(items.items(), start=1):
            label_key = QLabel(f"{key}")
            label_value = QLabel(f"{value}")    
            layout.addWidget(label_key, i, 0)
            layout.addWidget(label_value, i, 1)

        summary_window.setLayout(layout)
        summary_window.show()

        self.opened_windows.append(summary_window)
        summary_window.destroyed.connect(lambda: self.opened_windows.remove(summary_window))
    
    def update_buildnig_summary(self):
        self.building_summary.update_labels()

    def get_summary_object(self):
        return self.building_summary
    
    def get_building(self) -> str:
        return self.building
    
    def get_table(self):
        return self