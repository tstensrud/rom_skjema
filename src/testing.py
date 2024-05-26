import sys
from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton
import sqlite3

class TableWidgetDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.layout = QVBoxLayout()
        
        self.tableWidget = QTableWidget(5, 3)  # 5 rows, 3 columns
        self.tableWidget.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])
        for row in range(5):
            for column in range(3):
                self.tableWidget.setItem(row, column, QTableWidgetItem(f"Item {row+1}-{column+1}"))
        
        self.layout.addWidget(self.tableWidget)
        
        # Add a button to add a new row with data from an SQLite query
        self.addButton = QPushButton("Add New Row")
        self.addButton.clicked.connect(self.addNewRow)
        self.layout.addWidget(self.addButton)
        
        self.setLayout(self.layout)
        self.setWindowTitle("QTableWidget Add Row Example")
    
    def new_updated_row(self, row_count, data) -> None:
        self.tableWidget.insertRow(row_count)
        for column, value in enumerate(data):
            self.tableWidget.setItem(row_count, column, QTableWidgetItem(str(value)))
    
    def addNewRow(self):
        # Simulate an SQLite query that returns a tuple of data
        # For example purposes, let's use a hardcoded tuple
        data = ("New Item 6-1", "New Item 6-2", "New Item 6-3")
        
        # Get the current row count (i.e., the index where the new row will be inserted)
        row_count = self.tableWidget.rowCount()
        
        # Insert the new row with the data
        self.new_updated_row(row_count, data)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = TableWidgetDemo()
    demo.show()
    sys.exit(app.exec())
