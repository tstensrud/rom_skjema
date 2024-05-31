import os
import json
import sqlite3
from PyQt6.QtWidgets import QMessageBox
from prettytable import PrettyTable # for testing purposes
from contextlib import contextmanager

# To create single executable file
# change DB_PATH to "rooms.db"
# pyinstaller --onefile --add-data "db\rooms.db:." main.py
DB_PATH = "db/rooms.db"

# Error message
def error_message(error: str) -> None:
    QMessageBox.critical(None, "Error", f"SQLite error: {error}")

# Context manager to avoid the connect/close code in every method
@contextmanager
def get_cursor():
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()
    try:
        yield cursor
        connect.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        cursor.close()
        connect.close()

def create_room_table(building):
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {building} (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   bygg TEXT,
                   room_type TEXT NOT NULL,
                   floor TEXT NOT NULL,
                   roomnr TEXT NOT NULL,
                   roomname TEXT NOT NULL,
                   area REAL,
                   room_population INTEGER,
                   air_per_person REAL,
                   air_person_sum REAL,
                   air_emission REAL,
                   air_emission_sum REAL,
                   air_process REAL,
                   air_minimum REAL,
                   air_demand REAL,
                   air_supply REAL,
                   air_extract REAL,
                   air_chosen REAL,
                   ventilation_principle TEXT,
                   heat_exchange TEXT NOT NULL,
                   room_control TEXT NOT NULL,
                   notes TEXT,
                   db_teknisk TEXT,
                   db_rw_naborom TEXT,
                   db_rw_korridor TEXT,
                   system TEXT,
                   aditional TEXT
                   )
    """,)
    connect.commit()
    connect.close()

def get_all_tables():
    with get_cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
        result = cursor.fetchall()
        return [table[0] for table in result]

# Add units to the tabeldata
# E.g. area which i stored as 100 in the table will be return with a "m2" behind for better readability
def add_units_to_room_data(rows, single_room: bool) -> tuple:
    row_list_with_units = []
    if single_room is True:
        row_list = list(rows)
        row_list[5] = f"{row_list[5]} m2"
        row_list[6] = f"{row_list[6]} stk"
        row_list[7] = f"{row_list[7]} m3/h"
        row_list[8] = f"{row_list[8]} m3/h"
        row_list[9] = f"{row_list[9]} m3/m2"
        row_list[10] = f"{row_list[10]} m3/h"
        row_list[11] = f"{row_list[11]} m3/h"
        row_list[12] = f"{row_list[12]} m3/h"
        row_list[13] = f"{row_list[13]} m3/h"
        row_list[14] = f"{row_list[14]} m3/h"
        row_list[15] = f"{row_list[15]} m3/m2"
        return tuple(row_list)
    else:
        for row in rows:
            row_list = list(row)
            row_list[5] = f"{row_list[5]} m2"
            row_list[6] = f"{row_list[6]} stk"
            row_list[7] = f"{row_list[7]} m3/h"
            row_list[8] = f"{row_list[8]} m3/h"
            row_list[9] = f"{row_list[9]} m3/m2"
            row_list[10] = f"{row_list[10]} m3/h"
            row_list[11] = f"{row_list[11]} m3/h"
            row_list[12] = f"{row_list[12]} m3/h"
            row_list[13] = f"{row_list[13]} m3/h"
            row_list[14] = f"{row_list[14]} m3/h"
            row_list[15] = f"{row_list[15]} m3/m2"
            row_list_with_units.append(tuple(row_list))
        return row_list_with_units
                       
# Add new room to database
def add_new_room_to_db(building: str, room_type: str, floor: str, roomnr: str, roomname: str, area: float, pop: int, air_pp: float, 
             air_per_person_sum: float, air_emission: float, air_emission_sum: float, air_process: float, 
             air_min: float, air_demand: float, air_supply: float, air_extract: float, air_chosen: float,
             ventilation_principle: str, heat_exchange: str, room_control: str, notes: str, 
             db_teknisk: str, db_rw_nabo: str, db_rw_korr: str, system: str, aditional: str) -> int:   
    with get_cursor() as cursor:
        query = f"""INSERT INTO {building} (
                    bygg,
                    room_type, 
                    floor, 
                    roomnr, 
                    roomname, 
                    area, 
                    room_population, 
                    air_per_person, 
                    air_person_sum, 
                    air_emission, 
                    air_emission_sum, 
                    air_process, 
                    air_minimum, 
                    air_demand, 
                    air_supply, 
                    air_extract,
                    air_chosen, 
                    ventilation_principle, 
                    heat_exchange,
                    room_control, 
                    notes, 
                    db_teknisk, 
                    db_rw_naborom, 
                    db_rw_korridor, 
                    system, 
                    aditional
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(query, (building, room_type, floor, roomnr, roomname, area, pop, air_pp, air_per_person_sum, air_emission, air_emission_sum,
                                air_process, air_min, air_demand, air_supply, air_extract, air_chosen, ventilation_principle,
                                heat_exchange, room_control, notes, db_teknisk, db_rw_nabo, db_rw_korr, system, aditional))
        query = f"""SELECT id FROM {building} WHERE roomnr = ?"""
        cursor.execute(query, (roomnr,))
        result = cursor.fetchone()
        return result
    
# Checks if room number in a building allready exists. No two rooms should have the same room number
def check_if_room_number_exists(room_number: str, building: str) -> bool:
    with get_cursor() as cursor:
        cursor.execute(f"SELECT * FROM {building} WHERE roomnr=?", (room_number,))
        result = cursor.fetchone()
        if result is not None:
            return True
        else:
            return False

# Returns all data from rooms
def get_all_room_data_table(building: str):
    with get_cursor() as cursor:
        cursor.execute(f"""SELECT bygg, room_type, floor, roomnr, roomname, area, 
                       room_population, air_per_person, air_person_sum, air_emission, air_emission_sum,
                       air_process, air_minimum, air_demand, air_supply, air_extract, 
                       air_chosen, ventilation_principle, heat_exchange, room_control, notes,
                       db_teknisk, db_rw_naborom, db_rw_korridor, system, aditional
                       FROM {building} 
                       """)
        result = cursor.fetchall()
        return result

# Returns all data stored for a specific room
def get_all_room_data(room_id: str, building: str):
    with get_cursor() as cursor:
        cursor.execute(f"SELECT * FROM {building} WHERE id = ?", (room_id,))
        result = cursor.fetchall()
        return result

# Returns data for a specific room. Only columns used in the main window tables are returned
def get_room_table_data(building: str, room_id: int):
    with get_cursor() as cursor:
        result = ()
        cursor.execute(f"""
                    SELECT id, bygg, floor, roomnr, roomname, area, room_population, air_per_person, 
                    air_person_sum, air_emission, air_emission_sum, air_process, air_demand,
                    air_supply, air_extract, air_chosen, heat_exchange, ventilation_principle,
                    room_control, system, aditional
                    FROM {building} 
                    WHERE id=?""", (room_id,))
        result = cursor.fetchone()
        return add_units_to_room_data(result, True)
    
# Delete room from table
def delete_room(building: str, room_id: int) -> None:
    with get_cursor() as cursor:    
        cursor.execute(f"""DELETE FROM {building} WHERE id=?""",(room_id,))
        print(f"Room {room_id} deleted")

# Get all data from rooms that are to be shown in the table on the main window
def get_all_rooms(building: str):
    with get_cursor() as cursor:
        rows = []
        query = f"""
            SELECT id, bygg, floor, roomnr, roomname, area, room_population, air_per_person, 
            air_person_sum, air_emission, air_emission_sum, air_process, air_demand,
            air_supply, air_extract, air_chosen, heat_exchange, ventilation_principle,
            room_control, system, aditional 
            FROM {building}
            ORDER BY bygg ASC, floor ASC
            """
        cursor.execute(query)
        rows = cursor.fetchall()
        rows_with_unit_data = add_units_to_room_data(rows, False)
        return rows_with_unit_data

# Return the database column bame based on givne column index
def get_column_name(column_id: int) -> str:
    column_map = {
        0: "id",
        1: "bygg",
        2: "floor",
        3: "roomnr",
        4: "roomname",
        5: "area",
        6: "room_population",
        7: "air_per_person",
        8: "air_person_sum",
        9: "air_emission",
        10: "air_emission_sum",
        11: "air_process",
        12: "air_demand",
        13: "air_supply",
        14: "air_extract",
        19: "system",
        20: "aditional"
    }
    #print(f"Retrieved column {column_map.get(column_id)}")
    return column_map.get(column_id)

# Return the sum air volume for given building and floor
# Set floor to None if to sum up entire column
def get_sum_of_column_building_floor(building: str, floor: str, column: int) -> float:
    with get_cursor() as cursor:
        column_name: str = get_column_name(column)
        if floor is None:
            query = f"""SELECT SUM({column_name}) FROM {building}"""
            cursor.execute(query)
        else:
            query = f"""SELECT SUM({column_name}) FROM {building} WHERE floor = ?"""
            cursor.execute(query, (floor,))
        result = cursor.fetchone()
        return result[0]

def get_ventilation_system_per_building(building: str):
    with get_cursor() as cursor:
        cursor.execute(f"SELECT DISTINCT system FROM {building}")
        result = cursor.fetchall()
        return ([system[0] for system in result])

# Returns the total supply air volume of a given system
# Either for entire project or specific building
def get_total_air_supply_volume_system(building: str, system: str) -> float:
    volume = 0
    with get_cursor() as cursor:
        if building is None:
            pass
            # query all tables for given system
        else:
            cursor.execute(f"SELECT air_supply FROM {building} WHERE system = ?", (system,))
        result = cursor.fetchall()
        volumes = [volume[0] for volume in result]
        for val in volumes:
            volume += val
        return volume

# Returns the total extract air volumne of a given system
def get_total_air_extract_volume_system(building: str, system: str) -> float:
    with get_cursor() as cursor:
        if building is None:
            pass
            # query all tables for given system
        else:
            cursor.execute(f"SELECT air_extract FROM {building} WHERE system = ?", (system,))
        result = cursor.fetchall()
        volumes = [volume[0] for volume in result]
        volume = 0
        for val in volumes:
            volume += val
        return volume

# Load all room-types from a specification json-file
def load_room_types(specification: str):
    room_types = []
    json_file_path = os.path.join(os.path.dirname(__file__), "json", f"{specification}.json")
    with open(json_file_path) as jfile:
        data = json.load(jfile)
    if isinstance(data, dict):
        room_types = data.keys()
    return room_types

# Update table value
# Called when a user changes the value of a cell manually
def update_db_table_value(building: str, room_id: str, column_id: int, new_value) -> bool:
    with get_cursor() as cursor:
        column_name = get_column_name(column_id)       
        query = f"""UPDATE {building} 
                    SET {column_name} = ?
                    WHERE id = ? """
        cursor.execute(query, (new_value, room_id))
        print(f"Room-ID {room_id} changed column {column_name} to {new_value}")
    
    # recalculate all the values based on what value was changed
    if column_name == "air_supply":
        recalculate_based_on_supply(building, room_id)
    else:
        recalculate_all_values(building, room_id)
    
    return True

def get_single_cell_value(building: str, room_id: str, column: int):
    with get_cursor() as cursor:
        column_name: str = get_column_name(column)
        query = f"SELECT {column_name} FROM {building} WHERE id = ?"
        cursor.execute(query,(room_id,))
        result = cursor.fetchone()
        return result[0]


# Recalculate values when a table-value is updated
def recalculate_all_values(building: str, room_id: int) -> None:
    with get_cursor() as cursor:
        query = f""" SELECT 
                    area, 
                    room_population, 
                    air_per_person, 
                    air_emission, 
                    air_process
                    FROM {building}
                    WHERE id = ?
                    """
        cursor.execute(query,(room_id,))
        result = cursor.fetchone()
        if result is None:
            error_message("No values could be retrieved")
            return
        # Place result in variables
        area, room_population, air_per_person, air_emission, air_process = result
        
        # Recalculate values
        new_sum_air_pp = float(room_population * air_per_person)
        new_emission_sum = float(air_emission * area)
        new_air_demand = float(new_sum_air_pp + new_emission_sum + air_process)
        
        # Update database
        query_update = f"UPDATE {building} SET air_person_sum = ?, air_emission_sum = ?, air_demand = ? WHERE id = ?"
        cursor.execute(query_update, (new_sum_air_pp, new_emission_sum, new_air_demand, room_id))

# Recalculate air_chosen m3/m2 when air_supply is changed
def recalculate_based_on_supply(building: str, room_id: int):
    with get_cursor() as cursor:
        query = f"""SELECT  area, air_supply FROM {building} WHERE id=?"""
        cursor.execute(query, (room_id,))
        result = cursor.fetchall()
        for value in result:
            area, air_supply = value
        new_air_chosen = float(air_supply / area)
        update = f"UPDATE {building} SET air_chosen = ? WHERE id = ?"
        cursor.execute(update, (new_air_chosen, room_id))

def delete_table(table_name: str):
    with get_cursor() as cursor:
        query = f"DROP TABLE IF EXISTS {table_name}"
        cursor.execute(query)

# for testing purposes
def fetch_all_data(building):
    try:
        connect = sqlite3.connect(DB_PATH)
        cursor = connect.cursor()
        
        # Fetch all records
        cursor.execute(f'SELECT * FROM {building}')
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f'PRAGMA table_info({building})')
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]

        # Create a PrettyTable object
        table = PrettyTable()
        table.field_names = column_names

        # Add rows to the table
        for row in rows:
            table.add_row(row)

        # Print the table
        print(table)

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if connect:
            connect.close()

def new_column(column):
    try:
        connect = sqlite3.connect(DB_PATH)
        cursor = connect.cursor()
        
        # Construct the SQL statement
        query = f"ALTER TABLE rooms ADD COLUMN {column}"
        cursor.execute(query)
        
        connect.commit()
    
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if connect:
            connect.close()