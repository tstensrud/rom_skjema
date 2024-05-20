from tkinter import messagebox
import os
import json
from prettytable import PrettyTable
import sqlite3

DB_NAME = "./db/rooms.db"

def create_skok_table():
    connect = sqlite3.connect(DB_NAME)
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

# ADD NEW ROOM TO TABLE
def new_room(bygg: str, room_type: str, floor: str, roomnr: str, roomname: str, area: float, pop: int, air_pp: float, 
             air_per_person_sum: float, air_emission: float, air_emission_sum: float, air_process: float, 
             air_min: float, air_demand: float, air_supply: float, air_extract: float, air_chosen: float,
             ventilation_principle: str, heat_exchange: str, room_control: str, notes: str, 
             db_teknisk: str, db_rw_nabo: str, db_rw_korr: str, system: str, aditional: str) -> None:   
    try:
        connect = sqlite3.connect(DB_NAME)
        cursor = connect.cursor()
        insert = """INSERT INTO rooms (
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
        cursor.execute(insert, (bygg, room_type, floor, roomnr, roomname, area, pop, air_pp, air_per_person_sum, air_emission, air_emission_sum,
                                air_process, air_min, air_demand, air_supply, air_extract, air_chosen, ventilation_principle,
                                heat_exchange, room_control, notes, db_teknisk, db_rw_nabo, db_rw_korr, system, aditional))
        connect.commit()
    except sqlite3.Error as e:
        error_message(e)
    finally:
        if connect:
            connect.close()

# FIND IF ROOM-NUMBER ALREADY EXISTS.
def check_if_room_number_exists(room_number: str) -> bool:
    try:
        connect = sqlite3.connect(DB_NAME)
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM rooms WHERE roomnr=?", (room_number,))
        result = cursor.fetchone()
        if result is not None:
            return True
        else:
            return False
    except sqlite3.Error as e:
        error_message(e)
    finally:
        if connect:
            connect.close()

# RETURN ROOM DATA FROM SPECIFIC ROOM FOR TABLE ON MAIN WINDOW.
# USED WHEN ADDING NEW ROOM
def get_room(room_number: str):
    try:
        result = ()
        connect = sqlite3.connect(DB_NAME)
        cursor = connect.cursor()
        cursor.execute("""
                    SELECT id, bygg, floor, roomnr, roomname, area, room_population, air_per_person, 
                    air_person_sum, air_emission, air_emission_sum, air_process, air_demand,
                    air_supply, air_extract, air_chosen, heat_exchange, ventilation_principle,
                    room_control, system
                    FROM rooms 
                    WHERE roomnr=?""", (room_number,))
        result = cursor.fetchone()
        connect.commit()
        
        return add_units_to_room_data(result, True)
    except sqlite3.Error as e:
        error_message(e)
    finally:
        if connect:
            connect.close()
    
# DELETE ROOM FROM TABLE
def delete_room(room_number: str) -> None:
    try:
        connect = sqlite3.connect(DB_NAME)
        cursor = connect.cursor()    
        cursor.execute("""DELETE FROM rooms WHERE roomnr=?""",(room_number,))
        connect.commit()
    except sqlite3.Error as e:
        error_message(e)
    finally:
        if connect:
            connect.close()

# GET ALL DATA FROM ROOMS TO PLACE ON TABLE IN MAIN WINDOW
# ARGUMENT IS FOR WHAT LIST SHOULD BE SORTED BY
def get_all_rooms(order: str):
    try:
        rows = []
        connect = sqlite3.connect(DB_NAME)
        cursor = connect.cursor()
        if order is not None:
            query = f"""
                SELECT id, bygg, floor, roomnr, roomname, area, room_population, air_per_person, 
                air_person_sum, air_emission, air_emission_sum, air_process, air_demand,
                air_supply, air_extract, air_chosen, heat_exchange, ventilation_principle,
                room_control, system 
                FROM rooms 
                ORDER BY bygg ASC, floor ASC, {order} ASC
                """
        else:
            query = f"""
                SELECT id, bygg, floor, roomnr, roomname, area, room_population, air_per_person, 
                air_person_sum, air_emission, air_emission_sum, air_process, air_demand,
                air_supply, air_extract, air_chosen, heat_exchange, ventilation_principle,
                room_control, system 
                FROM rooms 
                ORDER BY bygg ASC, floor ASC
                """
        cursor.execute(query)
        rows = cursor.fetchall()
        connect.commit()
        rows_with_unit_data = add_units_to_room_data(rows, False)
        return rows_with_unit_data
    except sqlite3.Error as e:
        error_message(e)
    finally:
        if connect:
            connect.close()

# THIS METHOD ADDS UNITS TO THE ROOM-DATA FOR BETTER READABILITY IN THE TABLE
# E.G. AREA GETS ADDED m2
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

# ERROR MESSAGE FOR DB-QUERIES
def error_message(error: str) -> None:
    messagebox.showerror(title="Error", message=f"Error: {error}")

# RETURN SUM OF A COLUMN(s)
def get_sum_of_column(columns) -> float:
    try:
        column_sums = []
        connect = sqlite3.connect(DB_NAME)
        cursor = connect.cursor()
        for column in columns:
            query = f"""SELECT SUM({column}) FROM rooms"""
            cursor.execute(query)
            result = cursor.fetchone()
            connect.commit()
            column_sums.append(result[0])
        return column_sums
    except sqlite3.Error as e:
        error_message(e)
    finally:
        if connect:
            connect.close()

# RETURNS THE TOTAL AIR VOLUME OF GIVEN SYSTEM
def get_total_air_volume_system(system: str) -> float:
    try:
        connect = sqlite3.connect(DB_NAME)
        cursor = connect.cursor()
        cursor.execute("SELECT air_supply FROM rooms WHERE system = ?", (system,))
        result = cursor.fetchall()
        connect.commit()
        volumes = [volume[0] for volume in result]
        volume = 0
        for val in volumes:
            volume += val
        return volume
    except sqlite3.Error as e:
        error_message(e)
    finally:
        if connect:
            connect.close()

# GET ALL VENTILATION SYSTEMS
def get_ventilation_systems():
    try:
        connect = sqlite3.connect(DB_NAME)
        cursor = connect.cursor()
        cursor.execute("""
                       SELECT DISTINCT system 
                       FROM rooms
                       """)
        connect.commit()
        result = cursor.fetchall()
        return ([system[0] for system in result]) # return list of strings
    except sqlite3.Error as e:
        error_message(e)
    finally:
        if connect:
            connect.close()

# LOAD ALL ROOM TYPES IN A SPECIFICTAION FROM JSON FILE
def load_room_types(specification: str):
    room_types = []
    json_file_path = os.path.join(os.path.dirname(__file__), "json", f"{specification}.json")
    with open(json_file_path) as jfile:
        data = json.load(jfile)
    if isinstance(data, dict):
        room_types = data.keys()
    return room_types

# CHANGE SPECIFIC TABLE VALUE
# USED WHEN USER IS UPDATING A CELL MANUALLY
def update_table_value(room_id: str, column: str, new_value) -> bool:
    try:
        column_name = get_column_name(column)
        connect = sqlite3.connect(DB_NAME)
        cursor = connect.cursor()
        query = f"""UPDATE rooms 
                    SET {column_name} = ?
                    WHERE id = ?
        """
        cursor.execute(query, (new_value, room_id))
        connect.commit()
        return True
    except sqlite3.Error as e:
        error_message(e)
        return False
    finally:
        if connect:
            connect.close()

# RETURN COLUMN NAME BASED ON COLUMN_ID FROM TREEVIEW
# ONLY VALUES THAT SHOULD CHANGE ARE IN HERE.
def get_column_name(column_id) -> str:
    if column_id == "#2":
        return "bygg"
    elif column_id == "#3":
        return "floor"
    elif column_id == "#4":
        return "roomnr"
    elif column_id == "#5":
        return "roomname"
    elif column_id == "#6":
        return "area"
    elif column_id == "#7":
        return "room_population"
    elif column_id == "#8":
        return "air_per_person"
    elif column_id == "#9":
        return "air_emission"
    elif column_id == "#12":
        return "air_process"
    elif column_id == "#14":
        return "air_supply"
    elif column_id == "#15":
        return "air_extract"
    elif column_id == "#20":
        return "system"

def fetch_all_data():
    try:
        connect = sqlite3.connect(DB_NAME)
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
        connect = sqlite3.connect(DB_NAME)
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

