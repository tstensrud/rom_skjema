import os
import json
import sqlite3
from PyQt6.QtWidgets import QMessageBox
from prettytable import PrettyTable # for testing purposes
from contextlib import contextmanager

DB_PATH = "new_rooms.db"

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

def create_tables():
    with get_cursor() as cursor:
        query = """
            CREATE TABLE IF NOT EXISTS Buildings (
            BuildingID INTEGER PRIMARY KEY AUTOINCREMENT,
            BuildingName TEXT NOT NULL
            )
        """
        cursor.execute(query)

        query = """ 
            CREATE TABLE IF NOT EXISTS Rooms (
            RoomID INTEGER PRIMARY KEY AUTOINCREMENT,
            BuildingID INTEGER,
            RoomType TEXT NOT NULL,
            Floor TEXT NOT NULL,
            RoomNumber TEXT NOT NULL,
            RoomName TEXT NOT NULL,
            Area REAL,
            RoomPopulation INTEGER,
            FOREIGN KEY (BuildingID) REFERENCES Buildings(BuildingID)
            )
        """
        cursor.execute(query)

        query = """
            CREATE TABLE IF NOT EXISTS VentilationProperties (
            RoomID INTEGER,
            AirPerPerson REAL,
            AirPersonSum REAL,
            AirEmission REAL,
            AirEmissionSum REAL,
            AirProcess REAL,
            AirMinimum REAL,
            AirDemand REAL,
            AirSupply REAL,
            AirExtract REAL,
            AirChosen REAL,
            VentilationPrinciple TEXT,
            HeatExchange TEXT NOT NULL,
            RoomControl TEXT NOT NULL,
            Notes TEXT,
            DbTechnical TEXT,
            DbNeighbour TEXT,
            DBCorridor TEXT,
            System TEXT,
            Comments TEXT,
            FOREIGN KEY (RoomId) REFERENCES Rooms(RoomID)
            )
        """
        cursor.execute(query)

#create_tables()

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

#fetch_all_data("VentilationProperties")

def insert_room():
    with get_cursor() as cursor:
        buildingname = "A"
        query = """INSERT INTO Buildings (
                    BuildingName 
                    ) 
                    VALUES (?)"""
        cursor.execute(query, (buildingname,))

#insert_room()
fetch_all_data("Buildings")