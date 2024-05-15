import sys
from rooms import Room
import tkinter as tk
import db
from tkinter import ttk, messagebox, font

# sqlite


class MainWindow:
    def __init__(self):
        
        self.rooms = db.read_room_file()
        
        self.root = tk.Tk()
        self.root.title("Romskjema")
        self.root.geometry("2100x1024")
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)      

        # TABLE
        self.columns=("etasje", "romnr", "romnavn", "areal", "antall_pers", "m3_per_pers", 
                      "summert_pers", "emisjon", "sum_emisjon", "prossess", "dimensjonert", 
                      "tilluft", "avtrekk", "valgt", "gjenvinner", "ventilasjon", "styring", "system")
        self.room_table = ttk.Treeview(self.main_frame, columns=self.columns, show="headings")
        for column in self.columns:
            self.room_table.heading(column, text=column.capitalize().replace("_", " "))

        self.room_table.pack(side="left", fill="both", expand=True)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.room_table.yview)
        self.room_table.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        for i in range (len(self.columns)):
            if i == 0:
                self.room_table.column(self.columns[i], anchor="center")
            header_text = self.room_table.heading(self.columns[i], 'text')
            width = font.Font().measure(header_text)
            self.room_table.column(self.columns[i], width=width+50)
        
        # MENUBAR
        self.menu_bar = tk.Menu(self.root)
        self.menu_bar_options = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar_options.add_command(label="Fjern rom", command=self.remove_room, accelerator="Ctrl+D")
        self.menu_bar_options.add_command(label="Nytt rom", command=self.new_room_popup, accelerator="Ctrl+N")
        self.menu_bar.add_cascade(label="Valg", menu=self.menu_bar_options)

        # TEST ROOMs
        """ self.new_room("undervisningsrom","1", "A-12354", "Klasserom", 35, 150, "360.001")
        self.new_room("grupperom","1", "A-13254", "Grupperom", 35, 150, "360.001")
        self.new_room("vestibyle","1", "A-13333", "Vestibyle", 100, 250, "360.001")
        self.new_room("korridor","1", "A-9999", "korridor", 10, 100, "360.001")
        self.new_room("bibliotek","1", "A-13232", "bibliotek", 50, 500, "360.001") """

        # STARTUP
        self.insert_rooms_from_db()

        # KEYBOARD SHORTCUTS
        self.root.bind("<Control-n>", lambda event: self.new_room_popup())
        self.root.bind("<Control-d>", lambda event: self.remove_room())
        self.root.configure(menu=self.menu_bar)
        self.root.mainloop()

    # ADD NEW ROOM TO PROJECT
    def new_room_popup(self):
        # NEW ROOM WINDOW
        self.new_room_window = tk.Tk()
        self.new_room_window.title("Nytt rom")
        self.new_room_window.geometry("600x600")
        self.new_room_window_frame = tk.Frame(self.new_room_window)
        self.new_room_window_frame.pack(fill="both", expand=True)
        self.new_room_button = tk.Button(self.new_room_window_frame, text="Hey", command=lambda: self.add_new_room(True))
        self.new_room_button.pack()
        #new_room = Room(type, floor, room_number, name, population, area, system)
        #self.rooms.append(new_room)
        #self.room_table.insert('', tk.END, values=new_room.table_data)
        db.write_to_file(self.rooms)
    
    def add_new_room(self, multiple: bool) -> None:
        if multiple == True:
            self.new_room_window.destroy()
        
    # INSERT DATA FROM PICKLE-FILE UPON START UP
    def insert_rooms_from_db(self):
        for room in self.rooms:
            self.room_table.insert('', tk.END, values=room.table_data)

    # GET ROOM-INDEX BASED ON ROOM NUMBER, WHICH SHOULD BE UNIQUE
    def find_room(self, room_number):
        for i in range(len(self.rooms)):
            if self.rooms[i].get_room_number() == room_number:
                return i
    
    # REMOVE ROOM FROM PROJECT
    def remove_room(self) -> None:       
        if messagebox.askokcancel(title="Fjern rom", message="Vil du fjerne rom?"):
            for selected_item in self.room_table.selection():
                row_values = self.room_table.item(selected_item, 'values')
                room_number = row_values[1]
                self.rooms.pop(self.find_room(room_number))
                self.room_table.delete(selected_item)
            db.write_to_file(self.rooms)
        

if __name__ == "__main__":
    window = MainWindow()
        
        