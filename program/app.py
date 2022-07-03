"""
This is an upgraded version of my old app (todolist) which was created during Jan 6 2022.
In this version, the user creates Todo_lists where they store Tasks by answering a bunch of input fields.
This application has:
- seperate panels for Todo_lists and Tasks,
- creation windows for the creation of both Todo_lists and Tasks,
- a calendar to track activities throughout the day, 
- an alarm to notify if you miss any tasks

This application uses a variety of packages for running this software.
Please make sure you have all the neccessary packages and python 3 installed to start this program, 
without those this app will not run at all.
"""

import tkinter as tk
import sqlite3 as sql3
import tkcalendar

from datetime import datetime
from tkinter import ttk
from task import Todo_list, Task
from tkinter.messagebox import showerror, showinfo, askyesnocancel, showwarning
from taskdbmaker import delete_table_contents

# FIXME: Bugs in app.

# COLORS:
LIST_PANEL_COLOR = "#222C3C"
PAPER_COLOR = "#F0F0F0"
WHITE = "#FFFFFF"
BLACK = "#000000"
GOLD = "#FFC90E"
GRAY = "#696969"

# formatted current_date by removing a zero behind a number.
# example: instead of (11/03/07) it becomes: (11/3/7)
CURRENT_DATE = datetime.now().strftime('%m/%d/%y').replace('0', '')

# non 24-hour time format, example: 11:35 AM/PM
CURRENT_TIME = datetime.now().strftime('%I:%M %p')

def convert_to_bool(value):
    """Convers sqlite booleans (0s or 1s) into True or False."""
    converted = eval(value)
    return converted

def convert_time(time_data: str, initial_format: str, desired_format: str):
    """
    Gets time and its initial format to be converted into its desired output.

    Ex: 21:50 is converted to 9:50 PM.
    """
    conversion = datetime.strptime(time_data, initial_format)
    converted_time = datetime.strftime(conversion, desired_format)
    return converted_time


class App(tk.Tk):
    """Main part of the app."""
    def __init__(self):
        # Window properties
        tk.Tk.__init__(self)
        self.title("Task Man")
        self.geometry("800x600")
        self.resizable(False,False)

        # Invoking important methods
        self.menubar()
        self.todo_list_panel()
        self.task_panel()
        self.get_todo_lists()
        self.after(0, self.check_task_deadline())

        # Universal Keybinds
        self.bind("<Alt-q>", Todo_list_Maker)
        self.bind("<Alt-Q>", Todo_list_Maker)
        self.bind("<Alt-A>", Tasks_Maker)
        self.bind("<Alt-a>", Tasks_Maker)

    def menubar(self):
        # Menu commands
        menu = tk.Menu(self)
        menu.add_command(label="Settings", command=Settings)
        menu.add_command(label="Calendar", command=Calendar)
        menu.add_command(label="Help", command=Help)
        
        # Registering the menu to the app
        self.config(menu=menu)

    def todo_list_panel(self):
        # Widgets
        main_frm = tk.Frame(self, bg=LIST_PANEL_COLOR)
        title_frm = tk.Frame(master=main_frm, bg=LIST_PANEL_COLOR, borderwidth=5, relief=tk.RAISED)
        title_lbl = tk.Label(master=title_frm, bg=LIST_PANEL_COLOR, fg=WHITE, width=12, text="TODO LISTS", font="Verdana 24")

        self.todo_list_box = tk.Listbox(main_frm, bg=LIST_PANEL_COLOR, fg=WHITE, selectbackground=GOLD, selectforeground=BLACK, font="Verdana 11")
        self.todo_list_scroll = tk.Scrollbar(self.todo_list_box)

        btn_frm = tk.Frame(master=main_frm, bg=LIST_PANEL_COLOR)
        todo_list_delete_btn = tk.Button(master=btn_frm, bg=LIST_PANEL_COLOR, fg=WHITE, text="Delete", font="Verdana 12", borderwidth=3, activebackground=LIST_PANEL_COLOR, activeforeground=WHITE,
        width=9, command=self.delete_todo_lists)
        todo_list_add_btn = tk.Button(master=btn_frm, bg=LIST_PANEL_COLOR, fg=WHITE, text="Add List!", font="Verdana 12", borderwidth=3, activebackground=LIST_PANEL_COLOR, activeforeground=WHITE,
        width=14, command=Todo_list_Maker)

        # Keybinds
        self.todo_list_box.bind("<Double 1>", self.refresh_tasks)
        self.bind("<Control-D>", self.delete_todo_lists)
        self.bind("<Control-d>", self.delete_todo_lists)

        # Widget positioning
        main_frm.grid(row=0, column=0, sticky="ns")
        title_frm.grid(row=0, column=0)
        title_lbl.grid(row=0, column=0, pady=10)
        self.todo_list_box.grid(row=1, column=0, ipadx=117, ipady=210)
        
        self.todo_list_scroll.pack(side="right", fill="y")

        btn_frm.grid(row=2, column=0)
        todo_list_delete_btn.grid(row=2, ipady=8, column=0)
        todo_list_add_btn.grid(row=2, ipady=8, column=1)

    def task_panel(self):
        # Widgets
        sorties = ["Name", "Creation Date", "Deadline Date", "Deadline Time", "Completed"]
        main_frm = tk.Frame(self)

        title_frm = tk.Frame(master=main_frm)
        title_lbl = tk.Label(master=title_frm, text="Tasks:", font="Verdana 24")

        content_frm = tk.Frame(master=main_frm, borderwidth=5, relief=tk.SUNKEN)
        self.task_box = ttk.Treeview(master=content_frm, columns=sorties, show="headings", height=22)
        for index, sortie in enumerate(sorties):
            self.task_box.heading(index, text=sortie)
        self.task_box.column("Name", anchor=tk.CENTER, stretch=tk.NO, width=150)
        self.task_box.column("Creation Date", anchor=tk.CENTER, stretch=tk.NO, width=100)
        self.task_box.column("Deadline Date", anchor=tk.CENTER, stretch=tk.NO, width=100)
        self.task_box.column("Deadline Time", anchor=tk.CENTER, stretch=tk.NO, width=100)
        self.task_box.column("Completed", anchor=tk.CENTER, stretch=tk.NO, width=69)
        self.task_box_scroll = tk.Scrollbar(self.task_box)
        
        btn_frm = tk.Frame(master=main_frm)
        refresh_btn = ttk.Button(master=btn_frm, text="Refresh", width=15, command=self.refresh_tasks)
        task_delete_btn = ttk.Button(master=btn_frm, text="Delete", width=15, command=self.delete_tasks)
        task_add_btn = ttk.Button(master=btn_frm, text="Add", width=15, command=Tasks_Maker)
        mark_task_done_btn = ttk.Button(master=btn_frm, text="Mark as Done", width=15, command=self.mark_task_done)
        
        self.task_box.config(yscrollcommand=self.task_box_scroll.set)

        # Keybinds
        self.bind("<Control-m>", self.mark_task_done)
        self.bind("<Control-M>", self.mark_task_done)
        self.bind("<Alt-D>", self.delete_tasks)
        self.bind("<Alt-d>", self.delete_tasks)
        
        # Widget positioning
        main_frm.grid(row=0, column=1, ipady=270, ipadx=220, sticky="ns")
        
        title_frm.grid(row=0, column=0, pady=10, ipady=5)
        title_lbl.grid(row=0, column=0, padx=215)
        
        content_frm.grid(row=1, column=0)
        self.task_box.grid(row=0, column=0, ipadx=260, ipady=208)
        self.task_box_scroll.pack(side="right", fill="y")

        btn_frm.grid(row=2, column=0)
        refresh_btn.grid(row=0, column=0, ipadx=15, ipady=10)
        task_delete_btn.grid(row=0, column=1, ipadx=15, ipady=10)
        task_add_btn.grid(row=0, column=2, ipadx=15, ipady=10)
        mark_task_done_btn.grid(row=0, column=3, ipadx=15, ipady=10)

    def get_todo_lists(self):
        """Connects to database then formats data and inserts it to the Task panel."""
        
        conn = sql3.connect("database/taskdatabase.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM Todo_lists")
        data = cur.fetchall()
        conn.close()

        for val in data:
            self.todo_list_box.insert(tk.END,": ".join(val))
        self.todo_list_box.config(yscrollcommand=self.todo_list_scroll.set)
        
    def delete_todo_lists(self, event=None):
        """
        Prompts user if he REALLY wants to delete a Todo list. Then removes the list and its contents from the database itself.
        
        First it checks if the name of a Todo list is not an empty string, then proceeds to delete tasks and itself.
        """
        selected_todo_list = self.todo_list_box.get(tk.ANCHOR) # Name of Todo list and it's creation date
        splitted_values = selected_todo_list.split(":") # Splits todo_list and its respective date
        selected_todo_list_name = splitted_values[0] # Shows only the name of the Todo list

        if len(selected_todo_list) >= 1:
            prompt = askyesnocancel("Are you sure?", f"Are you sure you want to remove {selected_todo_list_name} from the list?")
            if prompt:
                
                conn = sql3.connect("database/taskdatabase.db")
                cur = conn.cursor()
                
                cur.execute("SELECT name FROM Tasks WHERE parent IS (?)", [selected_todo_list]) 
                todo_list_contents = cur.fetchall()
                cur.executemany("DELETE FROM Tasks WHERE name IS (?)", todo_list_contents)

                cur.execute("DELETE FROM Todo_lists WHERE name IS (?)", [selected_todo_list_name])
                conn.commit()
                conn.close()

                self.refresh_todo_lists()
                self.refresh_tasks()
                showinfo("Todo_list deleted", f"{selected_todo_list_name} has been deleted from the list.")
        else:
            showerror("Invalid command", "Select a Todo list to delete.")

    def refresh_todo_lists(self):
        """Deletes then re-inserts Todo_lists to avoid duplication."""
        self.todo_list_box.delete(0, tk.END)
        self.get_todo_lists()

    def get_tasks(self, event=None):
        """
        Gets child tasks of a highlighted Todo_list.
        It fetches all relevant Task values from <taskdatabase.db>
        """
        selected_todo_list = self.todo_list_box.get(tk.ANCHOR)
        conn = sql3.connect("database/taskdatabase.db")
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM Tasks WHERE parent IS (?)", [selected_todo_list])
        for (task_parent, task_name, task_creation_date, task_deadline_date, task_deadline_time, task_is_completed) in cur.fetchall():
            # Converts 1s and 0s to booleans
            if task_is_completed == "0":
                task_is_completed = False
            elif task_is_completed == "1":
                task_is_completed = True

            self.task_box.insert("", "end", values=(task_name, task_creation_date, task_deadline_date, task_deadline_time, task_is_completed))
        conn.close()

        self.task_box.config(yscrollcommand=self.task_box_scroll.set)

    def delete_tasks(self, event=None):
        """
        Deletes a highlighted Task instance by getting its name and comparing it with the ones in <taskdatabase.db>. 
        If the names match, a deletion is commited and notifies the user. 
        It will raise an invalid command error if the user tries to use the Task deletion button for other things.
        """
        try:
            # Fetches task
            selected_task = self.task_box.focus()
            selected_task_values = self.task_box.item(selected_task, "values")
            selected_task_name = selected_task_values[0]

            prompt = askyesnocancel("Are you sure?", f"Are you sure you want to remove {selected_task_name} from the list?")

            if prompt:
                conn = sql3.connect("database/taskdatabase.db")
                cur = conn.cursor()
                
                cur.execute("DELETE FROM Tasks WHERE name IS (?)", [selected_task_name]) 
                conn.commit()
                conn.close()

                self.refresh_tasks()                
                showinfo("Task deleted", f"{selected_task_name} has been deleted from the list.")
        except IndexError:
            showerror("Invalid command", "Select a Task to Delete.")

    def refresh_tasks(self, event=None):
        """Similar with refresh_todo_lists method."""
        self.task_box.delete(*self.task_box.get_children())
        self.get_tasks()
        self.check_task_deadline()

    def mark_task_done(self, event=None):
        """Checks if Task is finished or not. Toggles it to either True or False."""
        try:
            # Fetches Task
            selected_task = self.task_box.focus()
            selected_task_values = self.task_box.item(selected_task, "values")
            selected_task_name = selected_task_values[0]
            selected_task_is_completed = eval(selected_task_values[4]) # Converts str to bool.
            
            conn = sql3.connect("database/taskdatabase.db")
            cur = conn.cursor()

            if not selected_task_is_completed:
                cur.execute("""UPDATE Tasks SET is_completed = (?) WHERE name IS (?)""", [True, selected_task_name])
            else:
                cur.execute("""UPDATE Tasks SET is_completed = (?) WHERE name IS (?)""", [False, selected_task_name])

            conn.commit()
            conn.close()

            self.refresh_tasks()

        except IndexError:
            showerror("Invalid command", "Select a Task to Mark as Done.")

    def check_task_deadline(self):
        # FIXME: Rings alarm even though the time has not passed yet.
        """
        Checks if the tasks are overdue based on their date and time deadlines. If they are late and unfinished, 
        the program will show a warning message with the Task's name and its parent Todo list.
        """
        conn = sql3.connect("database/taskdatabase.db")
        cur = conn.cursor()        
        cur.execute("""SELECT * FROM Tasks""")
        tasks = cur.fetchall()
        conn.close()

        for task in tasks:
            parent, name, deadline_date, deadline_time, is_completed = task[0], task[1], task[3], task[4], convert_to_bool(task[5])

            if not is_completed:   
                if CURRENT_DATE > deadline_date:
                    showwarning("Missed Task", f"It appears that you've missed: {name} in {parent}")
                elif CURRENT_DATE == deadline_date: 
                    # FIXME: considers task as late even if it's ahead of due and deadline time is earlier than current time.
                    current = convert_time(CURRENT_TIME, "%I:%M %p", "%H:%M")
                    converted_deadline_time = convert_time(deadline_time, "%I:%M %p", "%H:%M")
                    
                    if current >= converted_deadline_time:
                        showwarning("Missed Task", f"It appears that you've missed: {name} in {parent}")


class Todo_list_Maker(tk.Toplevel):
    """A window for creating Todo_lists"""
    def __init__(self, event=None):
        # Window properties
        tk.Toplevel.__init__(self)
        self.title("Create a list!")
        self.resizable(False,False)

        # Invoking important methods
        self.todo_list_creation_window()

    def todo_list_creation_window(self):
        # Widgets
        title_frm = tk.Frame(self)
        select_name_lbl = tk.Label(master=title_frm, text="Create Todo List:", font="Verdana 18")
        
        content_frm = tk.Frame(self)
        entry_lbl = tk.Label(master=content_frm, text="Name:", font="Verdana 14")
        self.name_entry = tk.Entry(master=content_frm, font="Roboto 12", borderwidth=3, relief=tk.SUNKEN)

        btn_frm = tk.Frame(self)
        confirm_btn = ttk.Button(master=btn_frm, text="Confirm", command=self.is_empty)

        # Keybinds
        self.bind("<Return>", self.is_empty)

        # Widget positioning
        title_frm.grid(row=1, column=0)
        select_name_lbl.grid(row=0, column=0)

        content_frm.grid(row=2, column=0, padx=5, pady=10)
        entry_lbl.grid(row=0, column=0)
        self.name_entry.grid(row=0, column=1)

        btn_frm.grid(row=3, column=0, padx=5, pady=10, sticky="e")
        confirm_btn.grid(row=0, column=0)

    def is_empty(self, event=None):
        if len(self.name_entry.get()) <= 0:
            showerror("Empty input", "Fill in all inputs!")
        else:
            self.has_duplicates()

    def has_duplicates(self):
        """Checks for name duplicates by waiting for sqlite3 to invoke an IntegrityError exception."""
        name = self.name_entry.get()
        try: 
            self.create_todo_list()
        except sql3.IntegrityError:
            showerror("Duplicate!", f"{name} already exists!")

    def create_todo_list(self):
        """Utilizes user data to create a new Todo_list class then saves the data to <taskdatabase.db>."""
        name = self.name_entry.get()
        new_todo_list = Todo_list(name, CURRENT_DATE)

        conn = sql3.connect("database/taskdatabase.db")
        cur = conn.cursor()

        cur.execute("INSERT INTO Todo_lists VALUES (?, ?)", [new_todo_list.name, new_todo_list.creation_date])
        conn.commit()
        conn.close()

        app.refresh_todo_lists()

        showinfo("Todo list creation complete!", "Todo list created successfully.")


class Tasks_Maker(tk.Toplevel):
    """A window for creating Tasks"""
    def __init__(self, event=None):
        # Window properties
        tk.Toplevel.__init__(self)
        self.title("Append Tasks to list!")
        self.resizable(False,False)

        # Invoking important methods
        self.tasks_creation_window()

    def tasks_creation_window(self):
        # Widgets
        choices = (app.todo_list_box.get(0, tk.END))
        lbls = ["Todo list:", "Name:", "Creation Date:", "Deadline(Date):", "Deadline(Time):"]

        title_frm = tk.Frame(self)
        title = tk.Label(master=title_frm, text="Create a Task:", font="Verdana 20")

        self.content_frm = tk.Frame(self)
        for index, text in enumerate(lbls):
            labels = tk.Label(master=self.content_frm, text=text, font="Verdana 12")
            labels.grid(row=index, column=0, pady=10)
        self.todo_list_selection = ttk.Combobox(self.content_frm, values=choices, font="Roboto 12")
        self.name_entry = tk.Entry(master=self.content_frm, font="Roboto 12", borderwidth=3, relief=tk.SUNKEN, width=22)
        self.creation_date_result = tk.Label(master=self.content_frm, text=f"{CURRENT_DATE}", font="Roboto 12")
        self.deadline_date_entry = tkcalendar.DateEntry(master=self.content_frm, font="Roboto 12", width=20)
        self.deadline_time_entry = tk.Entry(master=self.content_frm, font="Roboto 12", borderwidth=3, relief=tk.SUNKEN, width=22)

        btn_frm = tk.Frame(self)
        clear_btn = ttk.Button(master=btn_frm, text="Clear", width=12, command=self.clear_input)
        confirm_btn = ttk.Button(master=btn_frm, text="Confirm", width=12, command=self.is_empty)

        # Keybinds
        for widget in self.content_frm.winfo_children():
            if widget.winfo_class() == "Entry" or widget.winfo_class() == "TEntry" or widget.winfo_class() == "TCombobox":
                widget.bind_all("<Return>", self.is_empty)

        # Widget positioning
        title_frm.grid(row=0, column=0)
        title.grid(row=0, column=0, padx=95, ipady=10)

        self.content_frm.grid(row=1, column=0)
        self.todo_list_selection.grid(row=0, column=1)
        self.name_entry.grid(row=1, column=1)
        self.creation_date_result.grid(row=2, column=1)
        self.deadline_date_entry.grid(row=3, column=1)
        self.deadline_time_entry.grid(row=4, column=1)

        btn_frm.grid(row=2, column=0, padx=5, pady=15, sticky="e")
        clear_btn.grid(row=0, column=0)
        confirm_btn.grid(row=0, column=1)
    
    def clear_input(self):
        """Checks for input fields in a specified frame then removes their input according to their widget type."""
        for widget in self.content_frm.winfo_children():
            if widget.winfo_class() == "Entry" or widget.winfo_class() == "TEntry":
                widget.delete(0, tk.END)
            elif widget.winfo_class() == "TCombobox":
                widget.set("")

    def is_empty(self, event=None):
        """
        Unlike Todo_list_Maker.is_empty method, this checks for every widget in content_frm that's considered an input field which are:
        - an Entry,
        - a TEntry.
        - a TCombobox,
        
        And checks if they all have input. If not it outputs an error message. But for some reason it outputs 3, therefore a counter was added
        to limit the amount of error pop-ups to 1. Else it moves on to check for duplicates.
        """
        counter = 1
        for widget in self.content_frm.winfo_children():
            if widget.winfo_class() == "Entry" or widget.winfo_class() == "TEntry" or widget.winfo_class() == "TCombobox":
                if len(widget.get()) <= 0 and counter < 2:
                    showerror("Empty input", "Fill in all inputs!")
                    counter += 1
                elif len(widget.get()) >= 0 and counter < 2:
                    self.validate_deadline_time()
                    counter += 1

    def validate_deadline_time(self):
        """Checks for valid time input which is (hh/mm am_pm)."""
        format = "%I:%M %p" # Should look like: ex 10:30 AM/PM
        deadline_time = self.deadline_time_entry.get()
        try:
            datetime.strptime(deadline_time, format)
            self.create_task()
        except ValueError:
            showerror("Invalid time", "Invalid time input! Please enter something like this:\nEx: 11:30 AM")

    def create_task(self):
        """
        Gets user input as Task data and is saves it to <taskdatabase.db>, 
        then highlights the updated Todo_list and displays a success message.
        """
        parent = self.todo_list_selection.get()

        name = self.name_entry.get()
        creation_date = self.creation_date_result.cget("text")
        deadline_date = self.deadline_date_entry.get()
        deadline_time = self.deadline_time_entry.get()
        new_task = Task(parent, name, creation_date, deadline_date, deadline_time)
        
        conn = sql3.connect("database/taskdatabase.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO Tasks VALUES (?, ?, ?, ?, ?, ?)",
        [new_task.parent, new_task.name, new_task.creation_date, new_task.deadline_date, new_task.deadline_time, new_task.is_completed])
        conn.commit()
        conn.close()
        
        app.refresh_tasks()
        showinfo("Task creation complete!", "Task created successfully.")


class Calendar(tk.Toplevel):
    def __init__(self):
        # Window properties
        tk.Toplevel.__init__(self)
        self.title("Calendar")
        self.geometry("550x550")
        self.resizable(False,False)

        # Invoking important methods
        self.calendar_panel()
        self.tasks_today_panel()

    def calendar_panel(self):
        # Widgets
        main_frm = tk.Frame(self, borderwidth=4, relief=tk.SUNKEN)
        self.calendar = tkcalendar.Calendar(master=main_frm)

        # Widget positioning
        main_frm.grid(row=0, column=0, padx=5, pady=5)
        self.calendar.grid(row=0, column=0, ipadx=140, ipady=70)

    def tasks_today_panel(self):
        # Widgets
        sorties = ["Todo list", "Name", "Deadline Time"]
        main_frm = tk.Frame(self)
        self.task_box = ttk.Treeview(master=main_frm, columns=sorties, show="headings", height=22)
        for index, sortie in enumerate(sorties):
            self.task_box.heading(index, text=sortie)
        self.task_box.column("Todo list", anchor=tk.CENTER, stretch=tk.NO, width=135)
        self.task_box.column("Name", anchor=tk.CENTER, stretch=tk.NO, width=140)
        self.task_box.column("Deadline Time", anchor=tk.CENTER, stretch=tk.NO, width=104)
        self.task_box_scroll = tk.Scrollbar(master=self.task_box)
        self.task_box.config(yscrollcommand=self.task_box_scroll.set)

        select_btn = ttk.Button(master=main_frm, text="Select Date", width=15, command=self.refresh_task_box)

        # Keybinds
        # Calls refresh_task method to always get the latest Task data
        self.bind("<Alt-s>", self.refresh_task_box)
        self.bind("<Alt-S>", self.refresh_task_box)

        # Widget positioning
        main_frm.grid(row=1, column=0, sticky="nsew")
        self.task_box.grid(row=0, column=0, ipadx=190, ipady=70, padx=5, pady=5)
        self.task_box_scroll.pack(side="right", fill="y")

        select_btn.grid(row=0, column=1, ipadx=15, ipady=10, pady=5, sticky="e")

    def get_tasks_based_on_day(self):
        """Selects already existing tasks based on the selected date and shows it in the task_box."""
        selected_date = self.calendar.get_date()

        conn = sql3.connect("database/taskdatabase.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM Tasks WHERE deadline_date IS (?)", [selected_date])

        for (task_parent, task_name, task_creation_date, task_deadline_date, task_deadline_time, task_is_completed) in cur.fetchall():
            self.task_box.insert("", "end", values=(task_parent, task_name, task_deadline_time))
        self.task_box.config(yscrollcommand=self.task_box_scroll.set)
        conn.close()

    def refresh_task_box(self, event=None):
        """Similar to app.refresh_tasks method."""
        self.task_box.delete(*self.task_box.get_children())
        self.get_tasks_based_on_day()


class Settings(tk.Toplevel):
    def __init__(self):
        # Window properties
        tk.Toplevel.__init__(self)
        self.title("Settings")
        self.geometry("800x610")
        self.resizable(False,False)
        
        # Invoking important methods
        self.selection_panel()
        self.options_panel()
        self.options_delete_all()

    def selection_panel(self):
        """A panel for selecting which options to open."""
        # Widgets
        sorties = ['Delete All', 'Version']
        main_frm = tk.Frame(self, bg=LIST_PANEL_COLOR)
        title_frm = tk.Frame(master=main_frm, bg=LIST_PANEL_COLOR, borderwidth=5, relief=tk.RAISED)
        title_lbl = tk.Label(master=title_frm, bg=LIST_PANEL_COLOR, fg=WHITE, text="SETTINGS", width=12, font="Verdana 24")

        self.settings_box = tk.Listbox(main_frm, bg=LIST_PANEL_COLOR, fg=WHITE, selectbackground=GOLD, selectforeground=BLACK, font="Verdana 11")
        self.settings_box_scroll = tk.Scrollbar(self.settings_box)
        for sortie in sorties:
            self.settings_box.insert(tk.END, sortie)

        # Keybinds
        self.settings_box.bind("<Double 1>", self.go_to_panel)

        # Widget positioning
        main_frm.grid(row=0, column=0, sticky="ns")
        title_frm.grid(row=0, column=0)
        title_lbl.grid(row=0, column=0, pady=10)
        self.settings_box.grid(row=1, column=0, ipadx=25, ipady=166)
        
    def options_panel(self):
        """This creates options_frm which manages all other option-related widgets."""
        # Widgets
        self.options_frm = tk.Frame(self)

        self.options_title_frm = tk.Frame(master=self.options_frm)
        self.options_title_lbl = tk.Label(master=self.options_title_frm, text="", font="Verdana 24")

        # Widget positioning
        self.options_frm.grid(row=0, column=1, sticky="ns")
        
        self.options_title_frm.grid(row=0, column=0, pady=10, ipady=5)
        self.options_title_lbl.grid(row=0, column=0, padx=200)

    def go_to_panel(self, event=None):
        """Opens a set of options based on the user's highlighted selection."""
        selected = self.settings_box.get(tk.ANCHOR)
        
        if selected == "Delete All":
            self.options_frm.grid_forget()
            self.options_panel()
            self.options_delete_all()
        if selected == "Version":
            self.options_frm.grid_forget()
            self.options_panel()
            self.options_version()
        
    def options_delete_all(self):
        """Shows the widgets that handle with deleting all Task and Todo lists."""
        # Configuring title name
        self.options_title_lbl.config(text="Delete All", font="Verdana 24")

        # Widgets
        content_frm = tk.Frame(self.options_frm)        
        delete_all_todo_lists_lbl = tk.Label(master=content_frm, text="Delete all saved Todo lists from app.", font="Verdana 12", justify=tk.LEFT)
        delete_all_todo_lists_btn = ttk.Button(master=content_frm, text="Delete All Todo lists", width=20, command=self.delete_all_todo_lists)
        delete_all_tasks_lbl = tk.Label(master=content_frm, text="Delete all saved Tasks from app.", font="Verdana 12", justify=tk.LEFT)
        delete_all_tasks_btn = ttk.Button(master=content_frm, text="Delete All Tasks", width=20, command=self.delete_all_tasks)

        # Widget positioning
        content_frm.grid(row=1, column=0)
        delete_all_todo_lists_lbl.grid(row=0, column=0, pady=10, sticky="w")
        delete_all_todo_lists_btn.grid(row=1, column=0, ipady=10, sticky="w")
        delete_all_tasks_lbl.grid(row=2, column=0, pady=10, sticky="w")
        delete_all_tasks_btn.grid(row=3, column=0, ipady=10, sticky="w")

    def options_version(self):
        # Configuring title name
        self.options_title_lbl.config(text="Version", font="Verdana 24")

        version = "2"

        # Widgets
        content_frm = tk.Frame(self.options_frm)
        version_num_lbl = tk.Label(master=content_frm, text=f"Version number: {version}", font="Verdana 12", justify=tk.LEFT)

        content_frm.grid(row=1, column=0)
        version_num_lbl.grid(row=0, column=0)

    def delete_all_todo_lists(self):
        """
        Deletes all Todo lists after prompting user.
        Also deletes Tasks from the Todo lists.
        """
        prompt = askyesnocancel("Are you sure?", f"Are you sure you want to delete all Todo lists?")
        if prompt:
            delete_table_contents("Todo_lists")
            delete_table_contents("Tasks")
            app.refresh_todo_lists()
            app.refresh_tasks()

            showinfo("Deleted all Todo lists", "Successfully deleted all Todo lists")
    
    def delete_all_tasks(self):
        """Deletes all Tasks data after prompting user."""
        prompt = askyesnocancel("Are you sure?", f"Are you sure you want to delete all Tasks")
        if prompt:
            delete_table_contents("Tasks")
            app.refresh_tasks()

            showinfo("Deleted all Tasks", "Successfully deleted all Tasks")


class Help(tk.Toplevel):
    def __init__(self):
        # Window properties
        tk.Toplevel.__init__(self)
        self.title("Help")
        self.geometry("800x610")
        self.resizable(False,False)

        # Invoking important methods
        self.selection_panel()
        self.help_panel()
        self.about_page()

    def selection_panel(self):
        """A panel for selecting which part of the app a user needs assistance."""
        # Widgets
        sorties = ['About', 'How to use', 'Todo lists', 'Tasks', 'Calendar', 'Controls/Shortcuts']
        main_frm = tk.Frame(self, bg=LIST_PANEL_COLOR)
        title_frm = tk.Frame(master=main_frm, bg=LIST_PANEL_COLOR, borderwidth=5, relief=tk.RAISED)
        title_lbl = tk.Label(master=title_frm, bg=LIST_PANEL_COLOR, fg=WHITE, text="HELP", width=12, font="Verdana 24")

        self.help_box = tk.Listbox(main_frm, bg=LIST_PANEL_COLOR, fg=WHITE, selectbackground=GOLD, selectforeground=BLACK, font="Verdana 11")
        self.help_box_scroll = tk.Scrollbar(self.help_box)
        for sortie in sorties:
            self.help_box.insert(tk.END, sortie)

        # Keybinds
        self.help_box.bind("<Double 1>", self.go_to_panel)

        # Widget positioning
        main_frm.grid(row=0, column=0, sticky="ns")
        title_frm.grid(row=0, column=0)
        title_lbl.grid(row=0, column=0, pady=10)
        self.help_box.grid(row=1, column=0, ipadx=25, ipady=176)

    def help_panel(self):
        """This creates help_frm which manages all other help-related widgets."""
        # Widgets
        self.help_frm = tk.Frame(self)
        self.help_title_frm = tk.Frame(master=self.help_frm)
        self.help_title_lbl = tk.Label(master=self.help_title_frm, text="", font="Verdana 24")

        # Widget positioning
        self.help_frm.grid(row=0, column=1, sticky="ns")
        self.help_title_frm.grid(row=0, column=0, pady=10, ipady=5)
        self.help_title_lbl.grid(row=0, column=0, padx=150)

    def go_to_panel(self, event=None):
        """Like Settings.go_to_panel method, this opens the highlighted selection of the user based on what they selected."""
        selected = self.help_box.get(tk.ANCHOR)
        
        if selected == "About":
            self.help_frm.grid_forget()
            self.help_panel()
            self.about_page()
        elif selected == "How to use":
            self.help_frm.grid_forget()
            self.help_panel()
            self.how_to_use_page()
        elif selected == "Todo lists":
            self.help_frm.grid_forget()
            self.help_panel()
            self.todo_lists_page()
        elif selected == "Tasks":
            self.help_frm.grid_forget()
            self.help_panel()
            self.tasks_page()
        elif selected == "Calendar":
            self.help_frm.grid_forget()
            self.help_panel()
            self.calendar_page()
        elif selected == "Controls/Shortcuts":
            self.help_frm.grid_forget()
            self.help_panel()
            self.controls_page()

    def about_page(self):
        # Configuring title name
        self.help_title_lbl.config(text="About the App:", font="Verdana 24")

        # Text
        about = """
        This app is my improved version of an old Todo list app. 
        It was created during January 6 2022. In this new rendition, the user
        creates a Todo list to hold Task items and Tasks to fulfill. They require
        the user to input a bunch of data to create them. A notification system
        exists where it notifies the user if they forget to do a Task. 
        """

        # Widgets
        content_frm = tk.Frame(master=self.help_frm)
        about_lbl = tk.Label(master=content_frm, text=about, font="Verdana 10", justify=tk.LEFT)

        # Widget positioning
        content_frm.grid(row=1, column=0, sticky="w")
        about_lbl.grid(row=0, column=0)

    def how_to_use_page(self):
        # Text
        how_to_use = """
        In order to use this app, you must create activties that you would like
        to remember.
        """ 
        
        todo_list_title = "Creating Todo lists:"
        todo_list = """
        To begin, create a Todo list by pressing Add List.
        it will store all of your tasks there. Give it a name and press confirm.
        no duplicates are allowed.
        """

        task_title = "Creating Tasks:"
        task = """
        Then press Add at the right side of the app. A 'Create a Task' 
        window will open. Then fill in the following blanks and press 
        confirm.

        These are what each Entry needs:
        - Todo list: A pre-existing Todo list to store the Task,
        - Name: A name to identify the Task,
        - Creation Date: Automatically filled, does not need input,
        - Deadline Date: The Task's day of deadline,
        - Deadline Time: The Task's deadline in Time, example: 11:00 AM/PM.
        """

        finish_title = "Finishing a Task:"
        finish = """
        If you've finished a Task, select the 'Mark as Done' button to
        update the Task's state to 'Done'. If a Task is 'Completed',
        the program will not alert you if it reaches its deadline.
        It can also be toggled back to 'Incomplete' if you want to
        be notified if you reach its deadline.
        """

        # Configuring title name
        self.help_title_lbl.config(text="How to use:")

        # Widget
        content_frm = tk.Frame(master=self.help_frm)

        how_to_use_lbl = tk.Label(master=content_frm, text=how_to_use, font="Verdana 10", justify=tk.LEFT)
        todo_list_title_lbl = tk.Label(master=content_frm, text=todo_list_title, font="Verdana 12", justify=tk.LEFT)
        todo_list_lbl = tk.Label(master=content_frm, text=todo_list, font="Verdana 10", justify=tk.LEFT)
        task_title_lbl = tk.Label(master=content_frm, text=task_title, font="Verdana 12", justify=tk.LEFT)
        task_lbl = tk.Label(master=content_frm, text=task, font="Verdana 10", justify=tk.LEFT)
        finish_title_lbl = tk.Label(master=content_frm, text=finish_title, font="Verdana 12", justify=tk.LEFT)
        finish_lbl = tk.Label(master=content_frm, text=finish, font="Verdana 10", justify=tk.LEFT)

        # Widget positioning
        content_frm.grid(row=1, column=0)
        how_to_use_lbl.grid(row=0, column=0, sticky="w")
        todo_list_title_lbl.grid(row=1, column=0, padx=39, sticky="w")
        todo_list_lbl.grid(row=2, column=0, sticky="w")
        task_title_lbl.grid(row=3, column=0, padx=39, sticky="w")
        task_lbl.grid(row=4, column=0, sticky="w")
        finish_title_lbl.grid(row=5, column=0, padx=39, sticky="w")
        finish_lbl.grid(row=6, column=0, sticky="w")

    def todo_lists_page(self):
        # Text
        desc = """
        Todo lists are items where you can store Tasks there. They are 
        identified with a user-generated name and its date of creation.
        
        - Commands related to Todo lists:
        - Creating a Todo list by pressing Add List,
        - Deleting one by pressing Delete, note that it also deletes.
        """

        # Widgets
        self.help_title_lbl.config(text="Todo lists:")

        content_frm = tk.Frame(master=self.help_frm)
        todo_lists_lbl = tk.Label(master=content_frm, text=desc, font="Verdana 10", justify=tk.LEFT)

        # Widget positioning
        content_frm.grid(row=1, column=0)
        todo_lists_lbl.grid(row=0, column=0, sticky="w")

    def tasks_page(self):
        # Text
        desc = """
        Tasks are objectives that the user has to complete within a
        selected set deadline, both date and time. The user will be
        notified if a Task is incomplete and it's past its deadline.

        These are the data required to create a Task:
        - Todo list: A pre-existing Todo list to store the Task,
        - Name: A name to identify the Task,
        - Creation Date: Automatically filled, does not need input,
        - Deadline Date: The Task's day of deadline,
        - Deadline Time: The Task's deadline in Time, example: 11:00 AM/PM.

        Commands related to Tasks:
        - Creating Tasks by clicking 'Add',
        - Deleting Tasks by clicking 'Delete',
        - Refreshing Tasks by clicking 'Refresh',
        - Toggling Task completion by clicking 'Mark as Done'
        """
        
        # Configuring title name
        self.help_title_lbl.config(text="Tasks:")

        # Widgets
        content_frm = tk.Frame(master=self.help_frm)
        tasks_lbl = tk.Label(master=content_frm, text=desc, font="Verdana 10", justify=tk.LEFT)

        # Widget positioning
        content_frm.grid(row=1, column=0)
        tasks_lbl.grid(row=0, column=0, sticky="w")

    def calendar_page(self):
        # Text
        desc = """
        The calendar is a tool that the user can use to see which
        tasks have the same deadline compared to a selected date.
        This helps the user in sorting out which tasks they have to
        do within that date.

        Commands related to Calendars:
        - Selecting a date by clicking 'Select'
          This shows the tasks which have their deadlines in that
          date.
        """

        # Configuring title name
        self.help_title_lbl.config(text="Calendar:")

        # Widgets
        content_frm = tk.Frame(master=self.help_frm)
        calendar_lbl = tk.Label(master=content_frm, text=desc, font="Verdana 10", justify=tk.LEFT)

        # Widget positioning
        content_frm.grid(row=1, column=0)
        calendar_lbl.grid(row=0, column=0, sticky="w")

    def controls_page(self):
        # Text
        desc = """
        I've added shortcuts to make the usage of the app less
        of a hassle. These are the ff:
        - Selecting an entry by Double clicking it,
        - Alt+q for creating a new Todo list,
        - Alt+a for creating a new Task,
        - Ctrl+d for deleting a Todo list,
        - Alt+d for deleting a Task,
        - Ctrl+m for marking a Task as done,
        - Alt+s for selecting a Date in calendar, 
        """

        # Configuring title name
        self.help_title_lbl.config(text="Controls:")

        content_frm = tk.Frame(master=self.help_frm)
        controls_lbl = tk.Label(master=content_frm, text=desc, font="Verdana 10", justify=tk.LEFT)

        # Widget positioning
        content_frm.grid(row=1, column=0)
        controls_lbl.grid(row=0, column=0, sticky="w")


if __name__ == "__main__":
    app = App()
    app.mainloop()