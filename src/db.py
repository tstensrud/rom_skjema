import pickle
from tkinter import messagebox

def write_to_file(object_list):
    try:
        with open("./db/rooms.pkl", "wb") as file:
            pickle.dump(object_list, file)
    except FileNotFoundError:
        messagebox.showerror(title="Error", message="Database not found")

def read_room_file():
    try:
        with open("./db/rooms.pkl", "rb") as file:
            rooms = pickle.load(file)
    except FileNotFoundError:
        messagebox.showerror(title="Error", message="Database not found")
    return rooms