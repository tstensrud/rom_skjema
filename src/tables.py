from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt

from db_operations import get_all_rooms, update_db_table_value

class RoomTable(QTableWidget):
    def __init__ (self, building):
        self.building = building

        # These columns should not be editable
        self.locked_columns =  [0,7,8,9,10,12,15,16,17,18]

        # Define column headers
        self. columns=["rom-id", "Bygg", "Etasje", "Romnr", "Romnavn", "Areal", "Antall_pers", "Luft per pers", 
                    "Sum personer", "Emisjon", "Sum emisjon", "Prosess", "Dimensjonert", 
                    "Tilluft", "Avtrekk", "Valgt", "Gjenvinner", "Prinsipp", "Styring", "System"]
        
        # Get all rooms for this building
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
        self.horizontalHeader().sectionClicked.connect(self.sort_rows) # for click on header

    # Change double click listener to ensure locked cells are uneditable
    def mouseDoubleClickEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid() and index.column() in self.locked_columns:
            return
        super().mouseDoubleClickEvent(event)
    
    # Insert data from databse
    def insert_data_from_db(self) -> None:
        for row, row_data in enumerate(self.rooms):
            for col, value in enumerate(row_data):               
                self.setItem(row, col, QTableWidgetItem(str(value)))

    # When cell is changed
    def changed_cell(self, item) -> str:
        row = item.row()
        column = str(item.column())
        room_id = self.item(row,0).text()
        new_value = int(item.text())
        print(column)
        update_db_table_value(room_id, column, new_value)

    
    # sort rows when one of the headers are clicked
    def sort_rows(self, section):
        sortable_columns = [2,3,4,19]
        if section in sortable_columns:
            self.sortItems(section, Qt.SortOrder.AscendingOrder)

    # Return the table object
    def get_table(self):
        return self