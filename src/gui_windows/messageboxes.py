from PyQt6.QtWidgets import QMessageBox

def information_box(title: str, message: str):
    box = QMessageBox()
    box.setIcon(QMessageBox.Icon.Information)
    box.setWindowTitle(title)
    box.setText(message)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    box.exec()