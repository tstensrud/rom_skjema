import json
import os
from db import new_room, load_room_types

class Room():
    def __init__(self, specification, building: str, room_type: str, floor: str, room_number: str, room_name: str,
                 population: int, area: float, system: str):
        
        self.specification = specification
        
        # LOAD JSON DATA
        json_file_path = os.path.join(os.path.dirname(__file__), "json", f"{self.specification}.json")
        with open(json_file_path) as jfile:
            data = json.load(jfile)
        
        # SET VARIABLES FROM JSON FILE ACCORDING TO CURRENT SPECIFICATION
        self.building = building
        self.room_type = room_type
        self.floor = floor
        self.room_number = room_number
        self.room_name = room_name
        self.area: float = area
        self.room_population: int = population
        self.air_per_person: float = data[f'{room_type}']['luftmengder']['m3_per_person']
        self.air_emission: float = data[f'{room_type}']['luftmengder']['m3_emisjon']
        self.air_process: float = data[f'{room_type}']['luftmengder']['m3_prossess']
        self.air_minimum: float = data[f'{room_type}']['luftmengder']['minimum_per_m2']
        self.regular_ventilation: bool = data[f'{room_type}']['luftfordeling']['omroring']
        self.displacement_ventilation: bool = data[f'{room_type}']['luftfordeling']['fortrengning']       
        self.heat_exchange = ""
        self.heat_exchange_rotate: str = data[f'{room_type}']['varmegjenvinner']['roterende']
        self.heat_exchange_plate: str = data[f'{room_type}']['varmegjenvinner']['plate']
        self.heat_exchange_battery: str = data[f'{room_type}']['varmegjenvinner']['batteri']
        if self.heat_exchange_rotate == True:
            self.heat_exchange += "R"
        if self.heat_exchange_plate == True:
            self.heat_exchange += "P"
        if self.heat_exchange_battery == True:
            self.heat_exchange += "B"
        self.room_control = {
            "vav": data[f'{room_type}']['styring']['vav'],
            "cav": data[f'{room_type}']['styring']['cav'],
            "temp": data[f'{room_type}']['styring']['temp'],
            "co2": data[f'{room_type}']['styring']['co2'],
            "movement": data[f'{room_type}']['styring']['bevegelse'],
            "moisture": data[f'{room_type}']['styring']['fukt'],
            "time": data[f'{room_type}']['styring']['tid']
        }
        self.room_controls = self.get_room_controls()
        self.notes: str = data[f'{room_type}']['presiseringer']
        self.activity: str = data[f'{room_type}']['aktivitet']
        self.sound = {
            "db_teknisk": data[f'{room_type}']['lydkrav']['teknisk'],
            "db_rw_naborom": data[f'{room_type}']['lydkrav']['rw_naborom'],
            "db_rw_korridor": data[f'{room_type}']['lydkrav']['rw_korridor']
        }
        self.additional: str = data[f'{room_type}']['kommentar']

        # INITIAL CALCULATIONS FOR VENTILATION VALUES
        self.sum_emissions = int(self.area * self.air_emission)
        self.sum_air_people = int(self.room_population * self.air_per_person)
        self.total_required_air_volume = int(self.sum_emissions + self.sum_air_people + self.air_process)
        self.minimum_air = int(self.air_minimum * self.area)
        self.chosen_air_supply: float = self.calculate_chosen_supply_volume()
        self.chosen_air_exhaust: float = self.chosen_air_supply
        self.sum_air_per_area = int(self.chosen_air_supply / self.area)
        self.ventilation_principle = self.get_ventilation_principle()
        self.system: str = system
        
        new_room(self.building, self.room_type, self.floor, self.room_number, self.room_name, self.area, self.room_population, self.air_per_person, self.sum_air_people, self.air_emission, self.sum_emissions,
                 self.air_process, self.minimum_air, self.total_required_air_volume, self.chosen_air_supply, self.chosen_air_exhaust, self.sum_air_per_area, self.ventilation_principle,
                 self.heat_exchange, self.room_controls, self.notes, self.sound['db_teknisk'], self.sound['db_rw_naborom'], self.sound['db_rw_korridor'], self.system, self.additional)
        
    
    def calculate_chosen_supply_volume(self) -> float:
        for i in range(self.total_required_air_volume, self.total_required_air_volume + 10):
            if i % 10 == 0:
                return i

    def get_ventilation_principle(self) -> str:
        if self.displacement_ventilation == True:
            return "Fortrengning"
        else:
            return "Omrøring"
    
    def get_room_controls(self) -> str:
        room_controls = ""
        if self.room_control['vav'] == True:
           room_controls += "VAV,"
        if self.room_control['cav'] == True:
            room_controls += "CAV,"
        if self.room_control['temp'] == True:
            room_controls += "T,"
        if self.room_control['co2'] == True:
            room_controls += "C,"
        if self.room_control['movement'] == True:
            room_controls += "B,"
        if self.room_control['moisture'] == True:
            room_controls += "F,"
        if self.room_control['time'] == True:
            room_controls +="Tid"
        return room_controls
