import os
import json as j
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, Toplevel
from tkinter.ttk import Progressbar
import threading
import logging
import plyer
from plyer import notification
import time as t
import runpy as rp
user = os.getlogin()

# Set up logging
logging.basicConfig(filename='reminder_app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class ReminderApp:
    def __init__(self):
        self.file_path = os.path.join(os.path.expanduser("~"), "Documents", "reminder_app_data.json")
        self.reminders = []
        self.load_data()
        self.check_overdue_reminders()
        self.root = tk.Tk()
        self.root.title("Reminder Manager")
        self.root.geometry("600x600")
        self.root.config(bg="#f0f0f0")
        self.is_dark_mode = False
        self.theme = "light"
        self.undo_stack = []
        self.redo_stack = []
        self.create_ui()

    def load_data(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self.reminders = j.load(f)
                # Ensure all reminders have the 'recurring' key
                for reminder in self.reminders:
                    if "recurring" not in reminder:
                        reminder["recurring"] = False

    def save_data(self):
        with open(self.file_path, "w") as f:
            j.dump(self.reminders, f, indent=4)

    def add_reminder(self):
        title = self.title_entry.get()
        description = self.description_entry.get()
        scheduled_yn = self.scheduled_var.get()
        recurring_yn = self.recurring_var.get()
        am_pm = self.am_pm_var.get()
        if scheduled_yn:
            if recurring_yn:
                recs = int(self.recurrences.get())
            else:
                recs = None
            year = self.year_var.get()
            month = self.month_var.get()
            day = self.day_var.get()
            if am_pm == "AM":
                if self.hour_var.get() == "12":
                    hour = "00"
                else:
                    hour = self.hour_var.get()
            else:
                if self.hour_var.get() == "12":
                    hour = "12"
                elif self.hour_var.get() == "01":
                    hour = "13"
                elif self.hour_var.get() == "02":
                    hour = "14"
                elif self.hour_var.get() == "03":
                    hour = "15"
                elif self.hour_var.get() == "04":
                    hour = "16"
                elif self.hour_var.get() == "05":
                    hour = "17"
                elif self.hour_var.get() == "06":
                    hour = "18"
                elif self.hour_var.get() == "07":
                    hour = "19"
                elif self.hour_var.get() == "08":
                    hour = "20"
                elif self.hour_var.get() == "09":
                    hour = "21"
                elif self.hour_var.get() == "10":
                    hour = "22"
                elif self.hour_var.get() == "11":
                    hour = "23"
            minute = self.minute_var.get()
            date_time = datetime.strptime(f"{year}-{month}-{day} {hour}:{minute}", "%Y-%m-%d %H:%M")
            
            reminder = {
                "title": title,
                "description": description,
                "scheduled": True,
                "datetime": date_time.strftime("%Y-%m-%d %H:%M"),
                "recurring": recurring_yn,
                "recurrences": recs
            }
        else:
            reminder = {
                "title": title,
                "description": description,
                "scheduled": False,
                "recurring": False
            }
        self.undo_stack.append((self.reminders.copy(), self.redo_stack.copy()))
        self.redo_stack.clear()
        self.reminders.append(reminder)
        self.save_data()
        self.clear_entries()
        messagebox.showinfo("Success", "Reminder added successfully!")
        self.update_reminder_list()



    def search_reminder(self):
        title = self.search_entry.get().lower()
        found = False
        for reminder in self.reminders:
            if reminder["title"].lower() == title:
                message = f"Title: {reminder['title']}\nDescription: {reminder['description']}"
                if reminder["scheduled"]:
                    message += f"\nScheduled: {reminder['datetime']}"
                else:
                    message += "\nScheduled: No"
                messagebox.showinfo("Reminder Found", message)
                found = True
                break
        if not found:
            messagebox.showinfo("Not Found", "No reminder found with the given title.")

    def remove_reminder(self):
        title = self.search_entry.get().lower()
        found = False
        for i, reminder in enumerate(self.reminders):
            if reminder["title"].lower() == title:
                self.undo_stack.append((self.reminders.copy(), self.redo_stack.copy()))
                del self.reminders[i]
                self.save_data()
                messagebox.showinfo("Success", "Reminder removed successfully!")
                self.update_reminder_list()
                found = True
                break
        if not found:
            messagebox.showinfo("Not Found", "No reminder found with the given title.")

    def check_overdue_reminders(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        for reminder in self.reminders:
            if reminder["scheduled"] and reminder["datetime"] < now:
                messagebox.showwarning("Overdue Reminders", "You have an overdue reminder.")
                if reminder["recurring"]:
                    if reminder["recurrences"] > 0:
                        now_d = datetime.now().isoweekday()
                        date_time = datetime.strptime(reminder["datetime"], "%Y-%m-%d %H:%M")
                        freq = reminder["req_freq"]
                        if freq == "ED":
                            new_date_time = date_time + timedelta(days=1)
                        elif freq == "EW":
                            new_date_time = date_time + timedelta(weeks=1)
                        elif freq == "EM":
                            new_date_time = date_time + timedelta(weeks=4.34524)
                        elif freq == "EY":
                            new_date_time = date_time + timedelta(weeks=52.1429)
                        elif freq == "EOD":
                            new_date_time = date_time + timedelta(days=2)
                        elif freq == "EOW":
                            new_date_time = date_time + timedelta(weeks=2)
                        elif freq == "EOM":
                            new_date_time = date_time + timedelta(weeks=8.69049)
                        elif freq == "EOY":
                            new_date_time = date_time + timedelta(weeks=104.357)
                        elif freq == "EWD":
                            if now_d < 5:
                                new_date_time = date_time + timedelta(days=1)
                            else:
                                pass
                        elif freq == "EWE":
                            if now_d == 6:
                                new_date_time = date_time + timedelta(days=1)
                            else:
                                pass
                        reminder["datetime"] = new_date_time.strftime("%Y-%m-%d %H:%M")
                        reminder["recurrences"] -= 1
                self.save_data()

    def clear_entries(self):
        self.title_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.scheduled_var.set(False)
        self.recurring_var.set(False)
        self.year_var.set("2025")
        self.month_var.set("01")
        self.day_var.set("01")
        self.hour_var.set("01")
        self.minute_var.set("00")
        self.search_entry.delete(0, tk.END)

    def update_reminder_list(self):
        self.reminder_listbox.delete(0, tk.END)
        for reminder in self.reminders:
            title = reminder["title"]
            if reminder["scheduled"]:
                title += f" (Scheduled: {reminder['datetime']})"
            if reminder["recurring"]:
                title += " (Recurring)"
            self.reminder_listbox.insert(tk.END, title)

    def toggle_theme(self):
        if self.theme == "light":
            self.theme = "dark"
        else:
            self.theme = "light"
        if self.theme == "light":
            self.root.config(bg="#333333")
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(bg="#333333", fg="white")
                elif isinstance(widget, tk.Entry):
                    widget.config(bg="#444444", fg="white")
                elif isinstance(widget, tk.Button):
                    widget.config(bg="#4CAF50", fg="white")
                elif isinstance(widget, tk.Checkbutton):
                    widget.config(bg="#333333", fg="white")
                elif isinstance(widget, tk.OptionMenu):
                    widget.config(bg="#444444", fg="white")
                elif isinstance(widget, tk.Listbox):
                    widget.config(bg="#444444", fg="white")
        else:
            self.root.config(bg="#f0f0f0")
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(bg="#f0f0f0", fg="black")
                elif isinstance(widget, tk.Entry):
                    widget.config(bg="white", fg="black")
                elif isinstance(widget, tk.Button):
                    widget.config(bg="#4CAF50", fg="white")
                elif isinstance(widget, tk.Checkbutton):
                    widget.config(bg="#f0f0f0", fg="black")
                elif isinstance(widget, tk.OptionMenu):
                    widget.config(bg="white", fg="black")
                elif isinstance(widget, tk.Listbox):
                    widget.config(bg="white", fg="black")

    def show_progress(self):
        self.progress = Progressbar(self.root, orient="horizontal", length=300, mode="indeterminate")
        self.progress.grid(row=11, column=0, columnspan=2, padx=10, pady=10)
        self.progress.start()

    def hide_progress(self):
        if self.progress:
            self.progress.stop()
            self.progress.grid_forget()

    def create_ui(self):
        # Preface
        messagebox.showinfo("Notice", "To make sure that you get notifications for your scheduled reminders, the app must be open at all times. If you are not using the app at the moment, minimize the window. If you cannot click the text entry, select an existing reminder or click 'add reminder'.")

        # Title
        tk.Label(self.root, text="Title:", bg=self.root.cget("bg"), font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.title_entry = tk.Entry(self.root, width=30, font=("Arial", 12))
        self.title_entry.grid(row=0, column=1, padx=10, pady=5)
        Tooltip(self.title_entry, "Enter the title of the reminder")

        # Description
        tk.Label(self.root, text="Description:", bg=self.root.cget("bg"), font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.description_entry = tk.Entry(self.root, width=30, font=("Arial", 12))
        self.description_entry.grid(row=1, column=1, padx=10, pady=5)
        Tooltip(self.description_entry, "Enter a description for the reminder")

        # Scheduled
        self.scheduled_var = tk.BooleanVar()
        self.scheduled_checkbutton = tk.Checkbutton(self.root, text="Scheduled", variable=self.scheduled_var, bg=self.root.cget("bg"), font=("Arial", 12))
        self.scheduled_checkbutton.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        Tooltip(self.scheduled_checkbutton, "Turn Scheduling On/Off")

        # Recurring
        self.recurring_var = tk.BooleanVar()
        self.recurring_checkbutton = tk.Checkbutton(self.root, text="Recurring", variable=self.recurring_var, bg=self.root.cget("bg"), font=("Arial", 12))
        self.recurring_checkbutton.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        Tooltip(self.recurring_checkbutton, "Turn Recurring On/Off")
        self.recurrences = tk.Entry(self.root, width=30, font=("Arial", 12))
        Tooltip(self.recurrences, """How many times the reminder should repeat. 
                Note: This count includes the first instance.""")
        self.rec_lab = tk.Label(self.root, text="# of recurrences:", bg=self.root.cget("bg"), font=("Arial", 12)).grid(row=2, column=2, padx=10, pady=5, sticky="w")
        self.recurrences.grid(row=2, column=3, padx=10, pady=5, sticky="w")
        self.freq_lab = tk.Label(self.root, text="Repeat every (hover over entry for help):")
        self.freq_lab.grid(row=3, column=2, padx=10, pady=5, sticky="w")
        self.freq = tk.Entry(self.root, width=30, font=("Arial", 12))
        self.freq.grid(row=3, column=3, padx=10, pady=5, sticky="w")
        Tooltip(self.freq, """Repeat: What to type
                Every Day: ED
                Every Week: EW
                Every Month: EM
                Every Year: EY
                Every Other Day: EOD
                Every Other Week: EOW
                Every Other Month: EOM
                Every Other Year: EOY
                Every Weekday: EWD
                Every Saturday and Sunday: EWE""")

        # Date and Time Frame
        date_time_frame = tk.Frame(self.root, bg=self.root.cget("bg"))
        date_time_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Date
        tk.Label(date_time_frame, text="Date:", bg=self.root.cget("bg"), font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")

        # Year
        self.year_var = tk.StringVar(value="2025")
        year_options = [str(year) for year in range(2025, 10000)]
        tk.Label(date_time_frame, text="Year:", bg=self.root.cget("bg"), font=("Arial", 12)).grid(row=0, column=1, padx=5, pady=5, sticky="e")
        tk.OptionMenu(date_time_frame, self.year_var, *year_options).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        tk.Label(date_time_frame, text="-", bg=self.root.cget("bg"), font=("Arial", 12)).grid(row=0, column=3, padx=0, pady=5)

        # Month
        self.month_var = tk.StringVar(value="01")
        month_options = [f"{i:02d}" for i in range(1, 13)]
        tk.Label(date_time_frame, text="Month:", bg=self.root.cget("bg"), font=("Arial", 12)).grid(row=0, column=4, padx=5, pady=5, sticky="e")
        tk.OptionMenu(date_time_frame, self.month_var, *month_options).grid(row=0, column=5, padx=5, pady=5, sticky="w")
        tk.Label(date_time_frame, text="-", bg=self.root.cget("bg"), font=("Arial", 12)).grid(row=0, column=6, padx=0, pady=5)

        # Day
        self.day_var = tk.StringVar(value="01")
        day_options = [f"{i:02d}" for i in range(1, 32)]
        tk.Label(date_time_frame, text="Day:", bg=self.root.cget("bg"), font=("Arial", 12)).grid(row=0, column=7, padx=5, pady=5, sticky="e")
        tk.OptionMenu(date_time_frame, self.day_var, *day_options).grid(row=0, column=8, padx=5, pady=5, sticky="w")

        # Time
        tk.Label(date_time_frame, text="Time:", bg=self.root.cget("bg"), font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")

        # Hour
        self.hour_var = tk.StringVar(value="01")
        hour_options = [f"{i:02d}" for i in range(1, 13)]
        tk.Label(date_time_frame, text="Hour:", bg=self.root.cget("bg"), font=("Arial", 12)).grid(row=1, column=1, padx=5, pady=5, sticky="e")
        tk.OptionMenu(date_time_frame, self.hour_var, *hour_options).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        tk.Label(date_time_frame, text=":", bg=self.root.cget("bg"), font=("Arial", 12)).grid(row=1, column=3, padx=0, pady=5)

        # Minute
        self.minute_var = tk.StringVar(value="00")
        minute_options = [f"{i:02d}" for i in range(0, 60)]
        tk.Label(date_time_frame, text="Minute:", bg=self.root.cget("bg"), font=("Arial", 12)).grid(row=1, column=4, padx=5, pady=5, sticky="e")
        tk.OptionMenu(date_time_frame, self.minute_var, *minute_options).grid(row=1, column=5, padx=5, pady=5, sticky="w")

        #AM PM
        self.am_pm_var = tk.StringVar(value="AM")
        options = ["AM", "PM"]
        tk.OptionMenu(date_time_frame, self.am_pm_var, *options).grid(row=1, column=6, padx=5, pady=5, sticky="w")
        # Add Button
        add_button = tk.Button(self.root, text="Add Reminder", command=self.add_reminder, bg="#4CAF50", fg="white", font=("Arial", 12))
        add_button.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
        Tooltip(add_button, "Add a new reminder")

        # Search
        tk.Label(self.root, text="Search:", bg=self.root.cget("bg"), font=("Arial", 12)).grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.search_entry = tk.Entry(self.root, width=30, font=("Arial", 12))
        self.search_entry.grid(row=5, column=1, padx=10, pady=5)
        Tooltip(self.search_entry, "Search for a reminder by title")

        # Search Button
        search_button = tk.Button(self.root, text="Search Reminder", command=self.search_reminder, bg="#008CBA", fg="white", font=("Arial", 12))
        search_button.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")
        Tooltip(search_button, "Search for a reminder")

        # Remove Button
        remove_button = tk.Button(self.root, text="Remove Reminder", command=self.remove_reminder, bg="#f44336", fg="white", font=("Arial", 12))
        remove_button.grid(row=7, column=0, columnspan=2, pady=10, sticky="ew")
        Tooltip(remove_button, "Remove a reminder")

        # Theme Toggle
        theme_button = tk.Button(self.root, text="Toggle Theme", command=self.toggle_theme, bg="#607D8B", fg="white", font=("Arial", 12))
        theme_button.grid(row=8, column=0, columnspan=2, pady=10, sticky="ew")
        Tooltip(theme_button, "Toggle between light and dark themes")

        # Reminder List
        tk.Label(self.root, text="Reminders:", bg=self.root.cget("bg"), font=("Arial", 12)).grid(row=9, column=0, padx=10, pady=5, sticky="e")
        self.reminder_listbox = tk.Listbox(self.root, width=70, height=10, font=("Arial", 12))
        self.reminder_listbox.grid(row=10, column=0, columnspan=2, padx=10, pady=5)

        # Update the list of reminders
        self.update_reminder_list()

        # Set focus to the title entry when the app starts
        self.title_entry.focus_set()

    def run(self):
        self.root.mainloop()
        while True:
            self.remind()
if __name__ == "__main__":
    rp.run_path(os.path.join(os.path.expanduser("~"), "Documents", "background_service.py"))
    app = ReminderApp()
    app.run()
