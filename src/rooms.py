import json
import os
import random
import string

from PyQt6.QtWidgets import (QMessageBox)

from db_operations import add_new_room_to_db, get_all_room_data, load_room_types

# Queries the database and returns all values for a room in json-format
def get_room_sql_data_to_json(room_id):
    data = get_all_room_data(room_id)
    columns = [
        "id", "Bygg", "Romtype", "Etasje", "Romnr", "Romnavn", "Areal", "Antall personer",
        "Luft per person", "Sum personbelastning",
        "Emissjon per m2", "Emissjon sum", "Prosess", "Minimum per m2", "Dimensjonert", "Tilluft",
        "Avtrekk", "Valgt per m2", "Ventilasjonsprinsipp", "Varmeveksler", "Styring", "Notater",
        "Lyd teknisk", "Lyd naborom", "Lyd korridor", "System", "Tilleggsinfo"
    ]
    try:
        return_list = [dict(zip(columns, row)) for row in data]
        json_data = json.dumps(return_list, indent=4)
        return json_data
    except TypeError as e:
        QMessageBox.critical(None, "Feil", f"Kunne ikke laste inn rom-data: {e}")
    except OverflowError as e:
        QMessageBox.critical(None, "Feil", f"Kunne ikke laste inn rom-data: {e}")
    except ValueError as e:
        QMessageBox.critical(None, "Feil", f"Kunne ikke laste inn rom-data: {e}")
    except Exception as e:
        QMessageBox.critical(None, "Feil", f"Kunne ikke laste inn rom-data: {e}")

# set all data for a new room and call the database-method for generating new room
def create_new_room(specification, building: str, room_type: str, floor: str, room_number: str, room_name: str,
                population: int, area: float, system: str) -> int:
    
    specification = specification
    
    # LOAD JSON DATA
    json_file_path = os.path.join(os.path.dirname(__file__), "json", f"{specification}.json")
    with open(json_file_path) as jfile:
        data = json.load(jfile)
    
    # SET VARIABLES FROM JSON FILE ACCORDING TO CURRENT SPECIFICATION
    building: str = building
    room_type: str = room_type
    floor: str = floor
    room_number: str = room_number
    room_name: str = room_name
    area: float = area
    room_population: int = population
    air_per_person: float = data[f'{room_type}']['luftmengder']['m3_per_person']
    air_emission: float = data[f'{room_type}']['luftmengder']['m3_emisjon']
    air_process: float = data[f'{room_type}']['luftmengder']['m3_prossess']
    air_minimum: float = data[f'{room_type}']['luftmengder']['minimum_per_m2']
    regular_ventilation: bool = data[f'{room_type}']['luftfordeling']['omroring']
    displacement_ventilation: bool = data[f'{room_type}']['luftfordeling']['fortrengning']       
    heat_exchange = ""
    heat_exchange_rotate: str = data[f'{room_type}']['varmegjenvinner']['roterende']
    heat_exchange_plate: str = data[f'{room_type}']['varmegjenvinner']['plate']
    heat_exchange_battery: str = data[f'{room_type}']['varmegjenvinner']['batteri']
    if heat_exchange_rotate == True:
        heat_exchange += "R"
    if heat_exchange_plate == True:
        heat_exchange += "P"
    if heat_exchange_battery == True:
        heat_exchange += "B"
    room_control = {
        "vav": data[f'{room_type}']['styring']['vav'],
        "cav": data[f'{room_type}']['styring']['cav'],
        "temp": data[f'{room_type}']['styring']['temp'],
        "co2": data[f'{room_type}']['styring']['co2'],
        "movement": data[f'{room_type}']['styring']['bevegelse'],
        "moisture": data[f'{room_type}']['styring']['fukt'],
        "time": data[f'{room_type}']['styring']['tid']
    }
    room_controls = get_room_controls(room_control)
    notes: str = data[f'{room_type}']['presiseringer']
    activity: str = data[f'{room_type}']['aktivitet']
    sound = {
        "db_teknisk": data[f'{room_type}']['lydkrav']['teknisk'],
        "db_rw_naborom": data[f'{room_type}']['lydkrav']['rw_naborom'],
        "db_rw_korridor": data[f'{room_type}']['lydkrav']['rw_korridor']
    }
    additional: str = data[f'{room_type}']['kommentar']

    # INITIAL CALCULATIONS FOR VENTILATION VALUES
    sum_emissions = int(area * air_emission)
    sum_air_people = int(room_population * air_per_person)
    total_required_air_volume = int(sum_emissions + sum_air_people + air_process)
    minimum_air = int(air_minimum * area)
    chosen_air_supply: float = calculate_chosen_supply_volume(total_required_air_volume)
    chosen_air_exhaust: float = chosen_air_supply
    sum_air_per_area = int(chosen_air_supply / area)
    
    ventilation_principle = ""
    if displacement_ventilation == True:
        ventilation_principle = "Fortrengning"
    else:
        ventilation_principle = "Omrøring"
    system: str = system
    
    new_room_id = add_new_room_to_db(building, room_type, floor, room_number, room_name, area, room_population, air_per_person, sum_air_people, air_emission, sum_emissions,
                air_process, minimum_air, total_required_air_volume, chosen_air_supply, chosen_air_exhaust, sum_air_per_area, ventilation_principle,
                heat_exchange, room_controls, notes, sound['db_teknisk'], sound['db_rw_naborom'], sound['db_rw_korridor'], system, additional)
    
    return new_room_id[0]

# round up to closest dividable by 10
# returns the first value dividable by 10, which is set as the
# chosen air volumne for the room.
def calculate_chosen_supply_volume(total_required_air_volume) -> float:
    for i in range(total_required_air_volume, total_required_air_volume + 10):
        if i % 10 == 0:
            return i

# set room controlls for room
def get_room_controls(room_control) -> str:
    room_controls = ""
    if room_control['vav'] == True:
        room_controls += "VAV,"
    if room_control['cav'] == True:
        room_controls += "CAV,"
    if room_control['temp'] == True:
        room_controls += "T,"
    if room_control['co2'] == True:
        room_controls += "C,"
    if room_control['movement'] == True:
        room_controls += "B,"
    if room_control['moisture'] == True:
        room_controls += "F,"
    if room_control['time'] == True:
        room_controls +="Tid"
    return room_controls

# generate a random room for testing purposes
def generate_room():
    buildings = ["A", "B", "C", "D", "E"]
    building = buildings[random.randint(0, len(buildings)-1)]
    floors = ["10", "20", "30", "40", "50"]
    floor = floors[random.randint(0, len(floors) - 1)]
    room_types = load_room_types("skok")
    room_type_list = []
    room_number = ""
    system_list = ["360.001", "360.002", "360.003", "360.004", "360.005", "360.006", "360.007", "360.008"]
    system = system_list[random.randint(0, len(system_list) - 1)]
    for _ in range(5):
        room_number += (random.choice(string.ascii_letters))
    for room in room_types:
        room_type_list.append(room)
    room_type = room_type_list[random.randint(0, len(room_type_list)-1)]
    create_new_room("skok", building, room_type, floor, room_number, room_type, random.randint(2,20), random.randint(5, 100),
         system) 