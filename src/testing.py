import tkinter as tk
from tkinter import ttk

class DraggableNotebook(ttk.Notebook):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self._active = None
        self.bind('<ButtonPress-1>', self.on_press, True)
        self.bind('<ButtonRelease-1>', self.on_release)
        self.bind('<B1-Motion>', self.on_motion)

    def on_press(self, event):
        element = self.identify(event.x, event.y)
        if "label" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self._active = index

    def on_release(self, event):
        self._active = None

    def on_motion(self, event):
        if self._active is None:
            return
        element = self.identify(event.x, event.y)
        if "label" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            if index != self._active:
                self._swap_tabs(self._active, index)
                self._active = index

    def _swap_tabs(self, i, j):
        tab_i = self.tab(i, "text")
        tab_j = self.tab(j, "text")
        self.tab(i, text=tab_j)
        self.tab(j, text=tab_i)

        # Swap the content of the tabs as well
        frame_i = self.nametowidget(self.tabs()[i])
        frame_j = self.nametowidget(self.tabs()[j])
        frame_i.pack_forget()
        frame_j.pack_forget()
        self.insert(i, frame_j)
        self.insert(j, frame_i)

class App:
    def __init__(self, root):
        self.root = root
        
        # Create a DraggableNotebook widget
        self.notebook = DraggableNotebook(root)
        self.notebook.pack(expand=True, fill='both')
        
        # Create frames for each tab
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        
        # Add frames to the notebook
        self.notebook.add(self.tab1, text='Tab 1')
        self.notebook.add(self.tab2, text='Tab 2')
        self.notebook.add(self.tab3, text='Tab 3')
        
        # Add some content to each tab
        ttk.Label(self.tab1, text="Content of Tab 1").pack(padx=20, pady=20)
        ttk.Label(self.tab2, text="Content of Tab 2").pack(padx=20, pady=20)
        ttk.Label(self.tab3, text="Content of Tab 3").pack(padx=20, pady=20)
        
        # Bind the NotebookTabChanged event to the on_tab_changed method
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
    def on_tab_changed(self, event):
        selected_tab = event.widget.index(event.widget.select())
        print(f"Selected tab: {selected_tab}")

# Create the main window
root = tk.Tk()
root.geometry("400x300")

app = App(root)

root.mainloop()
