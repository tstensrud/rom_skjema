from PyQt6.QtWidgets import (QGridLayout, QWidget, QLabel)
from db_operations import (get_ventilation_system_per_building, 
                           get_total_air_supply_volume_system, 
                           get_total_air_extract_volume_system)
from PyQt6.QtGui import QFont, QColor

class BuildingSummary(QWidget):
    def __init__ (self, building):
        super().__init__()
        self.building = building
        self.building_summaries = []
        self.layout = QGridLayout()
        self.initiate_labels()
        self.setLayout(self.layout)

    def initiate_labels(self):
        systems = get_ventilation_system_per_building(self.building)
        systems.sort()
        for i in range(len(systems)):
            building_summary = BuildingSummarySystem(self.building, systems[i])
            self.layout.addWidget(building_summary, 0, i)
            self.building_summaries.append(building_summary)
    
    def update_labels(self):
        for building_summary in self.building_summaries:
            building_summary.update_air_flows()

    def get_object(self):
        return self

class BuildingSummarySystem(QWidget):
    def __init__(self, building: str, system_name: str) -> None:
        super().__init__()
        self.building = building
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.font = QFont()
        self.font.setBold(True)
        self.system = system_name
        self.system_name = QLabel(self.system)
        self.text_label_supply = QLabel("Valgt tilluft:")
        self.text_label_extract = QLabel("Valgt avtrekk:")
        self.system_airflow_supply = f"{get_total_air_supply_volume_system(self.building, self.system)} m3/h"
        self.system_airflow_extract = f"{get_total_air_extract_volume_system(self.building, self.system)} m3/h"
        self.system_airflow_supply_label = QLabel(self.system_airflow_supply)
        self.system_airflow_extract_label = QLabel(self.system_airflow_extract)
        self.system_airflow_supply_label.setFont(self.font)
        self.system_airflow_extract_label.setFont(self.font)
        self.layout.setColumnStretch(1,2)
        self.layout.addWidget(self.system_name, 0, 0)
        self.layout.addWidget(self.text_label_supply, 1, 0)
        self.layout.addWidget(self.text_label_extract, 2, 0)
        self.layout.addWidget(self.system_airflow_supply_label, 1, 1)
        self.layout.addWidget(self.system_airflow_extract_label, 2, 1)
    
    def update_air_flows(self):
        self.system_airflow_supply_label.setText(f"{get_total_air_supply_volume_system(self.building, self.system)} m3/h")      
        self.system_airflow_extract_label.setText(f"{get_total_air_extract_volume_system(self.building, self.system)} m3/h")
