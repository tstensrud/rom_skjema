from rooms import Room
import tkinter as tk
import db_operations as db_operations
from tkinter import ttk, messagebox, font

class MainWindow:
    def __init__(self):
               
        self.root = tk.Tk()
        self.root.title("Romskjema")
        self.root.geometry("2300x1200")
        self.top_frame = tk.Frame(self.root, height=50)
        self.top_frame.pack(fill="x", side="top")
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(side="top", fill="both", expand=True)   
        self.top_frame.pack_propagate(False)   

        # TOP FRAME SETUP
        self.update_top_frame_summary()

        # TABLE FOR MAIN FRAME
        self.columns=("", "bygg", "etasje", "romnr", "romnavn", "areal", "antall_pers", "m3_per_pers", 
                      "summert_pers", "emisjon", "sum_emisjon", "prosess", "dimensjonert", 
                      "tilluft", "avtrekk", "valgt", "gjenvinner", "ventilasjon", "styring", "system")
        self.room_table = ttk.Treeview(self.main_frame, columns=self.columns, show="headings")
        self.room_table_style = ttk.Style()
        self.room_table_style.configure("Treeview.Heading", font=("Arial", 9, "bold"))

        for column in self.columns:
            self.room_table.heading(column, text=column.capitalize().replace("_", " "))

        self.room_table.pack(side="left", fill="both", expand=True)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.room_table.yview)
        self.room_table.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        for i in range (len(self.columns)):
            if i == 0:
                self.room_table.column(self.columns[i], width=0)
            header_text = self.room_table.heading(self.columns[i], 'text')
            width = font.Font().measure(header_text)
            self.room_table.column(self.columns[i], width=width+50)
        
        # MENUBAR
        self.menu_bar = tk.Menu(self.root)
        self.menu_bar_rooms = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar_rooms.add_command(label="Fjern rom", command=self.remove_room, accelerator="Ctrl+D")
        self.menu_bar_rooms.add_command(label="Nytt rom", command=self.new_room_popup, accelerator="Ctrl+N")
        self.menu_bar.add_cascade(label="Valg rom", menu=self.menu_bar_rooms)

        self.menu_bar_summary = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar_summary.add_command(label="Systemer")
        self.menu_bar.add_cascade(label="Oppsummering", menu=self.menu_bar_summary)

        # STARTUP
        self.update_room_list("floor")
        self.column_summaries()
        self.cell_entry = None # variable used for editing single cells in table

        # KEYBOARD SHORTCUTS AND KEYBINDS
        self.room_table.bind("<Button-1>", self.column_header_methods)
        self.room_table.bind("<Double-1>", self.edit_cell)
        self.root.bind("<Control-n>", lambda event: self.new_room_popup())
        self.root.bind("<Control-d>", lambda event: self.remove_room())
        self.root.configure(menu=self.menu_bar)
        self.root.mainloop()

    # SUMMARY OF SYSTEMS DATA. UPDATES ON ADDING AND REMOVING ROOMS
    def update_top_frame_summary(self):
        systems = db_operations.get_ventilation_systems()
        systems.sort()
        # clear all widgest
        for widget in self.top_frame.winfo_children():
            widget.destroy()
        # draw updated list of widgets
        for i in range(len(systems)):
            label_system = tk.Label(self.top_frame, text=f"{systems[i]}")
            label_volume = tk.Label(self.top_frame, text=f"{db_operations.get_total_air_volume_system(systems[i])} m3/h")
            label_system.grid(column=i, row=0, padx=10, pady=5)
            label_volume.grid(column=i, row=1, padx=10, pady=2)
    
    # SORTING TABLE BY CLICKING COLUMN HEADERS
    def column_header_methods(self, event):
        region = self.room_table.identify_region(event.x, event.y)
        if region == "heading":
            header = self.room_table.identify_column(event.x)
            if header == "#4":
                self.update_room_list("roomnr")
            elif header == "#20":
                self.update_room_list("system")
    
    # OPEN WINDOW FOR ADDING NEW ROOM
    def new_room_popup(self):
        # NEW ROOM WINDOW
        self.new_room_window = tk.Toplevel(self.root)
        self.new_room_window.title("Nytt rom")
        self.new_room_window.geometry("350x450")
        self.new_room_window_frame = tk.Frame(self.new_room_window)
        self.new_room_window_frame.pack(fill="both", expand=True)
        
        # combobox with room types
        rooms: str = []
        for room in db_operations.load_room_types("skok"):
            rooms.append(room)
        self.new_room_combobox = ttk.Combobox(self.new_room_window_frame, values=rooms)
        self.new_room_combobox.set("Romtype")
        self.new_room_combobox.grid(column=0, row=0, padx=5, pady=5)

        # labels
        self.new_room_building_lbl = tk.Label(self.new_room_window_frame, text="Bygg")
        self.new_room_floor_lbl = tk.Label(self.new_room_window_frame, text="Etasje")
        self.new_room_name_roomnr_lbl = tk.Label(self.new_room_window_frame, text="Romnr")
        self.new_room_name_roomname_lbl = tk.Label(self.new_room_window_frame, text="Romnavn")
        self.new_room_area_lbl = tk.Label(self.new_room_window_frame, text="Areal")
        self.new_room_name_people_lbl = tk.Label(self.new_room_window_frame, text="# Personer")
        self.new_room_name_system_lbl = tk.Label(self.new_room_window_frame, text="System")

        self.new_room_lbs = [self.new_room_building_lbl, self.new_room_floor_lbl, self.new_room_name_roomnr_lbl,
                             self.new_room_name_roomname_lbl, self.new_room_area_lbl,
                             self.new_room_name_people_lbl, self.new_room_name_system_lbl]
        for i in range(len(self.new_room_lbs)):
            self.new_room_lbs[i].grid(column=0, row=(i+1), padx=5, pady=5)

        # entries
        self.new_room_building_entry = tk.Entry(self.new_room_window_frame)
        self.new_room_floor_entry = tk.Entry(self.new_room_window_frame)
        self.new_room_roomnr_entry = tk.Entry(self.new_room_window_frame)
        self.new_room_roomname_entry = tk.Entry(self.new_room_window_frame)
        self.new_room_area_entry = tk.Entry(self.new_room_window_frame)        
        self.new_room_people_entry = tk.Entry(self.new_room_window_frame)
        self.new_room_system_entry = tk.Entry(self.new_room_window_frame)

        self.new_room_entries = [self.new_room_building_entry, self.new_room_floor_entry, self.new_room_roomnr_entry, self.new_room_roomname_entry,
                                 self.new_room_area_entry, self.new_room_people_entry, self.new_room_system_entry]
        for i in range(len(self.new_room_entries)):
            self.new_room_entries[i].grid(column=1, row=(i+1), padx=5, pady=5)

        self.last_row = len(self.new_room_lbs) + len(self.new_room_entries) + 2
        
        self.new_room_check_state = tk.IntVar()
        self.new_room_check = tk.Checkbutton(self.new_room_window_frame, text="Flere rom", variable=self.new_room_check_state)
        self.new_room_check.grid(column=1, row=self.last_row, padx=5, pady=5)

        self.new_room_button = tk.Button(self.new_room_window_frame, text="Legg til", command=self.add_new_room)
        self.new_room_button.grid(column=0, row=self.last_row, padx=5, pady=5)

    # MAKE EACH CELL EDITABLE
    def edit_cell(self, event):
        region = self.room_table.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.room_table.identify_column(event.x)
        row_id = self.room_table.identify_row(event.y)
        last_row = self.room_table.get_children()
        print(row_id)
        locked_columns={"#1", "#8", "#9", "#10", "#11", "#13", "#16", "#17", "#18", "#19"}
        if column in locked_columns:
            return
        item = self.room_table.item(row_id)
        row_values = self.room_table.item(row_id, "values")
        row_identifier = row_values[0] # stores the room id which is a unique indetifier for each room.
                
        col = int(column[1:]) - 1
        value = item["values"][col]
        
        if self.cell_entry:
            self.cell_entry.destroy()
        self.cell_entry = ttk.Entry(self.main_frame)
        self.cell_entry.insert(0, value)
        self.cell_entry.select_range(0, tk.END)
        self.cell_entry.focus()

        bbox = self.room_table.bbox(row_id, column)
        if bbox:
            self.cell_entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        self.cell_entry.bind('<Return>', lambda e: self.update_cell_value(row_id, column, row_identifier, value))
        self.cell_entry.bind('<FocusOut>', lambda e: self.update_cell_value(row_id, column, row_identifier, value))
    
    # CHANGE DATABASE ACCORDING TO NEW CELL VALUE
    def update_cell_value(self, row_id, column, row_identifier, old_value) -> None:
        new_value = self.cell_entry.get()
        if new_value == old_value:
            self.cell_entry.destroy()
            self.cell_entry = None
            return
        if db_operations.update_db_table_value(row_identifier, column, new_value):
            self.room_table.set(row_id, column, new_value)
            self.cell_entry.destroy()
            self.cell_entry = None
            self.update_room_list(None)
            self.update_top_frame_summary()
        else:
            messagebox.showerror(title="Feil", message="Kunne ikke oppdatere data")

    # ADD NEW ROOM AND CALL METHODS FOR SQL-ENTRY
    def add_new_room(self) -> None:
        multiple = self.new_room_check_state.get()
        building: str = self.new_room_building_entry.get()
        room_type: str = self.new_room_combobox.get()
        floor: str = self.new_room_floor_entry.get()
        room_number: str = self.new_room_roomnr_entry.get()
        if db_operations.check_if_room_number_exists(room_number):
            messagebox.showerror(title="Feil", message="Romnummer finnes allerede")
            return
        name: str = self.new_room_roomname_entry.get()
        
        try:
            population: int = int(self.new_room_people_entry.get())
        except ValueError:
            messagebox.showerror(title="Feil", message="Kun tall i antall personer")
            return
        
        try:
            area: float = float(self.new_room_area_entry.get())
        except ValueError:
            messagebox.showerror(title="Feil", message="Kun tall i areal")
            return
        
        system: str = self.new_room_system_entry.get()
        
        if room_type == "Romtype":
            messagebox.showerror(title="Feil", message="Velg romtype")
            return
        Room("skok", building, room_type, floor, room_number, name, population, area, system)
        self.update_room_list(None)
        

        if multiple == 0:
            self.update_top_frame_summary()
            self.new_room_window.destroy()
        else:
            self.update_top_frame_summary()
            self.new_room_roomnr_entry.delete(0, tk.END)
            self.new_room_roomname_entry.delete(0, tk.END)
            self.new_room_people_entry.delete(0, tk.END)
            self.new_room_area_entry.delete(0, tk.END)

    # LOAD ALL ROOMS FROM DATABASE
    # ARGUMENT IS FOR WHAT IT SHOULD BE SORTED AS
    def update_room_list(self, order) -> None:
        # clear table
        for item in self.room_table.get_children():
            self.room_table.delete(item)
        rooms = db_operations.get_all_rooms(order)
        
        # insert updated table values
        for room in rooms:
            self.room_table.insert('', tk.END, values=room)
        summary_column = self.column_summaries()
        self.room_table.insert('', tk.END, values=summary_column)
    
    # SUMMARIZES THE COLUMNS THAT NEED TO BE SUMMARIZED
    # ADDED TO BOTTOM OF TABLE
    def column_summaries(self) -> tuple:
        column_sums = db_operations.get_sum_of_column(["area", "air_demand", "air_supply", "air_extract"])
        column_tuple = ("Sum", "","", "", "",f"{column_sums[0]} m2", "", "", "", "", "", "", f"{column_sums[1]} m3/h", 
                        f"{column_sums[2]} m3/h", f"{column_sums[3]} m3/h", "", "", "", "", "", "")
        return column_tuple

    # REMOVE ROOM FROM PROJECT
    def remove_room(self) -> None:       
        if messagebox.askokcancel(title="Fjern rom", message="Vil du fjerne rom?"):
            for selected_item in self.room_table.selection():
                row_values = self.room_table.item(selected_item, 'values')
                room_number = row_values[3]
                db_operations.delete_room(room_number)
                self.room_table.delete(selected_item)
                self.update_top_frame_summary()
                self.update_room_list(None)

if __name__ == "__main__":
    window = MainWindow()
        
        