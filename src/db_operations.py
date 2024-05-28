import os
import json
import sqlite3
from PyQt6.QtWidgets import QMessageBox
from prettytable import PrettyTable # for testing purposes
from contextlib import contextmanager

DB_PATH = "./db/rooms.db"

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
        error_message(e)
    finally:
        cursor.close()
        connect.close()

def create_room_table():
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
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
    """)
    connect.commit()
    connect.close()

# Add new room to database
def add_new_room_to_db(bygg: str, room_type: str, floor: str, roomnr: str, roomname: str, area: float, pop: int, air_pp: float, 
             air_per_person_sum: float, air_emission: float, air_emission_sum: float, air_process: float, 
             air_min: float, air_demand: float, air_supply: float, air_extract: float, air_chosen: float,
             ventilation_principle: str, heat_exchange: str, room_control: str, notes: str, 
             db_teknisk: str, db_rw_nabo: str, db_rw_korr: str, system: str, aditional: str) -> int:   
    with get_cursor() as cursor:
        query = """INSERT INTO rooms (
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
        cursor.execute(query, (bygg, room_type, floor, roomnr, roomname, area, pop, air_pp, air_per_person_sum, air_emission, air_emission_sum,
                                air_process, air_min, air_demand, air_supply, air_extract, air_chosen, ventilation_principle,
                                heat_exchange, room_control, notes, db_teknisk, db_rw_nabo, db_rw_korr, system, aditional))
        query = """SELECT id FROM rooms WHERE roomnr = ?"""
        cursor.execute(query, (roomnr,))
        result = cursor.fetchone()
        return result
    
# Checks if room number in a building allready exists. No two rooms should have the same room number
def check_if_room_number_exists(room_number: str, building: str) -> bool:
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM rooms WHERE bygg = ? AND roomnr=?", (building, room_number,))
        result = cursor.fetchone()
        if result is not None:
            return True
        else:
            return False

# Returns all data stored for a specific room
def get_all_room_data(room_id: str):
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
        result = cursor.fetchall()
        return result

# Returns data for a specific room. Only columns used in the main window tables are returned
def get_room_table_data(room_id):
    with get_cursor() as cursor:
        result = ()
        cursor.execute("""
                    SELECT id, bygg, floor, roomnr, roomname, area, room_population, air_per_person, 
                    air_person_sum, air_emission, air_emission_sum, air_process, air_demand,
                    air_supply, air_extract, air_chosen, heat_exchange, ventilation_principle,
                    room_control, system
                    FROM rooms 
                    WHERE id=?""", (room_id,))
        result = cursor.fetchone()
        return add_units_to_room_data(result, True)
    
# Delete room from table
def delete_room(room_id: str) -> None:
    with get_cursor() as cursor:    
        cursor.execute("""DELETE FROM rooms WHERE id=?""",(room_id,))
        print(f"Room {room_id} deleted")

# Get all data from rooms that are to be shown in the table on the main window
def get_all_rooms(building: str):
    with get_cursor() as cursor:
        rows = []
        query = f"""
            SELECT id, bygg, floor, roomnr, roomname, area, room_population, air_per_person, 
            air_person_sum, air_emission, air_emission_sum, air_process, air_demand,
            air_supply, air_extract, air_chosen, heat_exchange, ventilation_principle,
            room_control, system 
            FROM rooms
            WHERE bygg = ?
            ORDER BY bygg ASC, floor ASC
            """
        cursor.execute(query, (building,))
        rows = cursor.fetchall()
        rows_with_unit_data = add_units_to_room_data(rows, False)
        return rows_with_unit_data

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

# Return the sum of a column
def get_sum_of_column(columns) -> float:
    with get_cursor() as cursor:
        column_sums = []
        for column in columns:
            query = f"""SELECT SUM({column}) FROM rooms"""
            cursor.execute(query)
            result = cursor.fetchone()
            column_sums.append(result[0])
        return column_sums

# Get all current ventilationsystems
def get_all_ventilation_systems():
    with get_cursor() as cursor:
        cursor.execute("SELECT DISTINCT system FROM rooms")
        result = cursor.fetchall()
        return ([system[0] for system in result]) # return list of strings

def get_ventilation_system_per_building(building):
    with get_cursor() as cursor:
        cursor.execute("SELECT DISTINCT system FROM rooms WHERE bygg = ?", (building,))
        result = cursor.fetchall()
        return ([system[0] for system in result])

# Returns the total supply air volume of a given system
def get_total_air_supply_volume_system(system: str, building: str) -> float:
    with get_cursor() as cursor:
        if building is None:
            cursor.execute("SELECT air_supply FROM rooms WHERE system = ?", (system,))
        else:
            cursor.execute("SELECT air_supply FROM rooms WHERE system = ? AND bygg = ?", (system, building))
        result = cursor.fetchall()
        volumes = [volume[0] for volume in result]
        volume = 0
        for val in volumes:
            volume += val
        return volume

# Returns the total extract air volumne of a given system
def get_total_air_extract_volume_system(system: str, building: str) -> float:
    with get_cursor() as cursor:
        if building is None:
            cursor.execute("SELECT air_extract FROM rooms WHERE system = ?", (system,))
        else:
            cursor.execute("SELECT air_extract FROM rooms WHERE system = ? AND bygg = ?", (system, building))
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
def update_db_table_value(room_id: str, column_id: str, new_value) -> bool:
    with get_cursor() as cursor:
        column_name = get_column_name(column_id)
        query = f"""UPDATE rooms 
                    SET {column_name} = ?
                    WHERE id = ? """
        cursor.execute(query, (new_value, room_id))
        print(f"Room-ID {room_id} changed column {column_name} to {new_value}")
    
    # recalculate all the values based on what value was changed
    if column_name == "air_supply":
        recalculate_based_on_supply(room_id)
    else:
        recalculate_all_values(room_id)
    
    return True

# Recalculate values when a table-value is updated
def recalculate_all_values(room_id) -> None:
    with get_cursor() as cursor:
        query = """ SELECT 
                    area, 
                    room_population, 
                    air_per_person, 
                    air_emission, 
                    air_process
                    FROM rooms
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
        query_update = "UPDATE rooms SET air_person_sum = ?, air_emission_sum = ?, air_demand = ? WHERE id = ?"
        cursor.execute(query_update, (new_sum_air_pp, new_emission_sum, new_air_demand, room_id))

# Recalculate air_chosen m3/m2 when air_supply is changed
def recalculate_based_on_supply(room_id):
    with get_cursor() as cursor:
        query = """SELECT  area, air_supply FROM rooms WHERE id=?"""
        cursor.execute(query, (room_id,))
        result = cursor.fetchall()
        for value in result:
            area, air_supply = value
        new_air_chosen = float(air_supply / area)
        update = "UPDATE rooms SET air_chosen = ? WHERE id = ?"
        cursor.execute(update, (new_air_chosen, room_id))

# Return the database column bame based on givne column index
def get_column_name(column_id) -> str:
    column_map = {
        "1": "bygg",
        "2": "floor",
        "3": "roomnr",
        "4": "roomname",
        "5": "area",
        "6": "room_population",
        "7": "air_per_person",
        "8": "air_emission",
        "11": "air_process",
        "13": "air_supply",
        "14": "air_extract",
        "19": "system"
    }
    return column_map.get(column_id)

# Returns list of buildings
def get_buildings():
    with get_cursor() as cursor:
        cursor.execute("SELECT DISTINCT bygg FROM rooms")
        result = cursor.fetchall()
        return ([building[0] for building in result])

# for testing purposes
def fetch_all_data():
    try:
        connect = sqlite3.connect(DB_PATH)
        cursor = connect.cursor()
        
        # Fetch all records
        cursor.execute('SELECT * FROM rooms')
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute('PRAGMA table_info(rooms)')
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