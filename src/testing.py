from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QMainWindow, QWidget
from PyQt6.QtCore import Qt
import sys

class RoomTable(QTableWidget):
    def __init__(self, building, rows=5, columns=3, locked_columns=None):
        super().__init__(rows, columns)
        self.building = building
        self.setHorizontalHeaderLabels(['Column 1', 'Column 2', 'Column 3'])
        self.locked_columns = locked_columns if locked_columns is not None else []

        for row in range(rows):
            for column in range(columns):
                item = QTableWidgetItem(f'{building} Cell {row+1},{column+1}')
                self.setItem(row, column, item)

    def mouseDoubleClickEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid() and index.column() in self.locked_columns:
            return  # Ignore the event if the column is locked
        super().mouseDoubleClickEvent(event)  # Call the base class implementation for other columns

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Room Manager")
        self.resize(800, 600)

        self.tables = []

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.generate_tab()

    def generate_tab(self) -> None:
        buildings = self.get_buildings()
        for i in range(len(buildings)):
            table = RoomTable(buildings[i], locked_columns=[0, 2])  # Lock columns 0 and 2
            self.tables.append(table)
            self.layout.addWidget(table)

    def get_buildings(self):
        # Replace with the actual logic to get buildings from the database
        return ["Building A", "Building B", "Building C"]

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
