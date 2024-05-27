from PyQt6.QtWidgets import (QGridLayout, QWidget, QLabel)
from db_operations import (get_ventilation_systems, 
                           get_total_air_supply_volume_system, 
                           get_total_air_extract_volume_system)

summary_objects = []

class Summary(QWidget):
    def __init__ (self):
        super().__init__()
        self.layout = QGridLayout()
        self.initiate_labels()
        self.setLayout(self.layout)

    def initiate_labels(self):
        systems = get_ventilation_systems()
        systems.sort()
        for i in range(len(systems)):
            system_name = QLabel(systems[i])
            system_airflow_supply = f"Tilluft: {get_total_air_supply_volume_system(systems[i])} m3/h"
            system_airflow_extract = f"Avtrekk: {get_total_air_extract_volume_system(systems[i])} m3/h"
            system_airflow_supply_label = QLabel(system_airflow_supply)
            system_airflow_extract_label = QLabel(system_airflow_extract)
            self.layout.addWidget(system_name, 0, i)
            self.layout.addWidget(system_airflow_supply_label, 1, i)
            self.layout.addWidget(system_airflow_extract_label, 2, i)
    
    
    def get_object(self):
        return self