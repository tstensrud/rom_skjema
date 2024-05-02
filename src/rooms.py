import json
import os
class Room():
    def __init__(self, room_type: str, floor: str, room_number: str, room_name: str,
                 population: int, area: float, system: str):
        json_file_path = os.path.join(os.path.dirname(__file__), "json", "skok.json")
        with open(json_file_path) as jfile:
            data = json.load(jfile)
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

        self.chosen_air_supply: float = 0
        self.chosen_air_exhaust = 0
        self.system: str = system

    def get_ventilation_sum_persons(self) -> float:
        return self.room_population * self.air_per_person

    def get_sum_emission(self) -> float:
        return self.area * self.air_emission

    def get_required_air(self) -> float:
        room_required_persons = self.room_population * self.air_per_person
        room_required_emissions = self.area * self.air_emission
        room_requirement = room_required_persons + room_required_emissions + self.air_process
        return room_requirement

    def get_minium_air(self) -> float:
        return self.air_minimum * self.area

    def get_air_per_area(self) -> float:
        return self.chosen_air_supply / self.area

    def get_ventilation_principle(self) -> str:
        if self.displacement_ventilation == False:
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
