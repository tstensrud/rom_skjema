import tkinter as tk
from tkinter import ttk

class EditableTreeviewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Editable Treeview Example")

        self.tree = ttk.Treeview(root, columns=("name", "age", "email"), show='headings')
        self.tree.heading("name", text="Name")
        self.tree.heading("age", text="Age")
        self.tree.heading("email", text="Email")

        # Insert sample data
        data = [("John Doe", "28", "john@example.com"),
                ("Jane Smith", "34", "jane@example.com"),
                ("Mike Brown", "45", "mike@example.com")]
        
        for item in data:
            self.tree.insert("", tk.END, values=item)

        self.tree.pack(expand=True, fill='both')

        # Bind the double-click event to start editing
        self.tree.bind('<Double-1>', self.on_double_click)

        self.entry = None

    def on_double_click(self, event):
        # Identify the region, column and row clicked
        region = self.tree.identify('region', event.x, event.y)
        if region != 'cell':
            return

        column = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        row_id = self.tree.identify_row(event.y)

        # Get the current value of the cell
        item = self.tree.item(row_id)
        col = int(column[1:]) - 1  # Get column index, -1 because columns start from #1
        value = item['values'][col]

        # Create an entry widget at the cell position
        if self.entry:
            self.entry.destroy()
        self.entry = ttk.Entry(self.root)
        self.entry.insert(0, value)
        self.entry.select_range(0, tk.END)
        self.entry.focus()
        
        bbox = self.tree.bbox(row_id, column)
        if bbox:
            self.entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])

        # Bind entry widget to update the cell value
        self.entry.bind('<Return>', lambda e: self.update_cell_value(row_id, column, col))
        self.entry.bind('<FocusOut>', lambda e: self.update_cell_value(row_id, column, col))

    def update_cell_value(self, row_id, column, col):
        new_value = self.entry.get()
        self.tree.set(row_id, column, new_value)
        self.entry.destroy()
        self.entry = None

if __name__ == "__main__":
    root = tk.Tk()
    app = EditableTreeviewApp(root)
    root.mainloop()
