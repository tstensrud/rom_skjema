import sys
from rooms import Room
import tkinter as tk
from tkinter import ttk, messagebox, font

# sqlite


class MainWindow:
    def __init__(self):
        
        self.rooms = []

        self.root = tk.Tk()
        self.root.title("Romskjema")
        self.root.geometry(f"2100x1024")
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

        for column in self.columns:
            header_text = self.room_table.heading(column, 'text')
            width = font.Font().measure(header_text)
            self.room_table.column(column, width=width+50)
        
        # MENUBAR
        self.menu_bar = tk.Menu(self.root)
        self.menu_bar_options = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar_options.add_command(label="Fjern rom", command=self.remove_room)
        self.menu_bar_options.add_command(label="Nytt rom", command=self.new_room)
        self.menu_bar.add_cascade(label="Valg", menu=self.menu_bar_options)

        # TEST ROOMs
        self.new_room("undervisningsrom","1", "A-12354", "Klasserom", 35, 150, "360.001")
        self.new_room("grupperom","1", "A-13254", "Grupperom", 35, 150, "360.001")
        self.new_room("vestibyle","1", "A-13333", "Vestibyle", 100, 250, "360.001")
        self.new_room("korridor","1", "A-9999", "korridor", 10, 100, "360.001")
        self.new_room("bibliotek","1", "A-13232", "bibliotek", 50, 500, "360.001")

        #self.root.bind("<Configure>", self.on_resize)
        self.root.configure(menu=self.menu_bar)
        self.root.mainloop()

    def on_resize(self, event):
        print("Resized")

    def new_room(self, type, floor, room_number, name, population, area, system):
        new_room = Room(type, floor, room_number, name, population, area, system)
        self.rooms.append(new_room)
        self.room_table.insert('', tk.END, values=new_room.table_data)
            
    
    # get room-index based on room_number from self.rooms-list
    def find_room(self, room_number):
        for i in range(len(self.rooms)):
            if self.rooms[i].get_room_number() == room_number:
                return i
    
    # remove room from table and from self.rooms
    def remove_room(self) -> None:       
        if messagebox.askokcancel(title="Fjern rom", message="Vil du fjerne rom?"):
            for selected_item in self.room_table.selection():
                row_values = self.room_table.item(selected_item, 'values')
                room_number = row_values[1]
                self.rooms.pop(self.find_room(room_number))
                self.room_table.delete(selected_item)

if __name__ == "__main__":
    window = MainWindow()
        
        