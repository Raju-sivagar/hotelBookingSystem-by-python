# File Name: gui.py
# Description: Handles all data persistence using SQLite. Responsible for storing, retrieving, updating, and deleting rooms and reservations in the Hotel Booking System database.
# Author: Piyumi Ediriweera
# Date: 2025-11-21

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import date
import os

# Import modules
from storage import Storage
from hotel import Hotel
from enums import RoomType, ReservationStatus

DB_NAME = "hotel.db"

class HotelGUI(tk.Tk):
    def __init__(self, storage: Storage, hotel: Hotel):
        super().__init__()
        self.title("Hotel Booking Dashboard")
        self.geometry("1000x650")
        self.storage = storage
        self.hotel = hotel

        #  Styling the Dashboard UI 
        style = ttk.Style(self)
        # This controls the visual style of widgets like buttons, frames, labels, treeviews, and notebook tabs in the GUI
        style.theme_use("clam")
        # style for the main frame container
        style.configure("TFrame", background="#21436E")
        # styles for the labels in small popup windows of the buttons (Add room, Edit room etc)
        style.configure("TLabel", background="#ffffff", foreground="#000000", font=("Segoe UI", 12, "bold"))
        # styles for the buttons in the above small popups(OK, Cancel)
        style.configure("TButton", background="#357ABD", foreground="white", font=("Segoe UI", 11))
        # style for header subnavigation buttons
        style.map("TButton",
                  background=[("active", "#2C9676")],
                  foreground=[("disabled", "#ccc")])
        # change the sidebar background colors,labels and button colors
        style.configure("Sidebar.TFrame", background="#21436E")
        style.configure("Sidebar.TLabel", background="#21436E", foreground="#fff", font=("Segoe UI", 16, "bold"))
        style.configure("Sidebar.TButton", background="#BEE9E8", foreground="#000000", font=("Segoe UI", 11, "bold"))
        style.map("Sidebar.TButton",
                  background=[('active', "#FFFBEA"), ('pressed', "#8AC6D1")])
        # header navigation background change
        style.configure("TNotebook", background="#5EC6E7", borderwidth=0)
        style.configure("TNotebook.Tab", background="#5EC6E7", foreground="white", font=("Segoe UI", 11, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", "#2C9676"), ("active", "#A3CEF1")],
                  foreground=[("selected", "#fff"), ("active", "#ffffff")])
        # data view background color
        style.configure("Treeview", background="#ffffff", foreground="#125B50", fieldbackground="#E3F2FD", font=("Segoe UI", 10))
        # data view grid background change
        style.map("Treeview", background=[("selected", "#35477D")])

        # calling the creat_widget() below to load all the UI frames when programme starts
        self.create_widgets()
        # reload all the data insetred
        self.refresh_all()

    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar frame
        sidebar = ttk.Frame(self, width=200, padding=(8, 12), style="Sidebar.TFrame")
        # use sticky ns to stretch the frame from top to bottom
        sidebar.grid(row=0, column=0, sticky="ns")
        # disabling the default behaviour with screen sizes and stick to the frame size even the inside label width are small
        sidebar.grid_propagate(False)

        # sidebar header menu position with 10 pixel vertical padding
        ttk.Label(sidebar, text="Menu", style="Sidebar.TLabel").pack(pady=(10,10))
        # When clicked, lambda: self.show_tab("rooms") switches the main display to the "Rooms" tab.
        ttk.Button(sidebar, text="Rooms", style="Sidebar.TButton", command=lambda: self.show_tab("rooms")).pack(fill="x", pady=4)
        # When clicked, lambda: self.show_tab("reservations") switches the main display to the "Reservations" tab.
        ttk.Button(sidebar, text="Reservations", style="Sidebar.TButton", command=lambda: self.show_tab("reservations")).pack(fill="x", pady=4)
        # When clicked programme will be closed.
        ttk.Button(sidebar, text="Quit", style="Sidebar.TButton", command=self.quit).pack(fill="x", pady=(30,4))

        # Main area
        # Creates a new ttk.Frame named main_frame as a child of the main window (self).
        main_frame = ttk.Frame(self, padding=(8,8))
        # Places the main_frame inside the window using the grid geometry manager. Positions it at row 0, column 1 (right side next to the sidebar at column 0).The "nsew" value makes the frame stretch to fill the space north, south, east, and west (i.e., expand in all directions).
        main_frame.grid(row=0, column=1, sticky="nsew")

        # Creates a ttk.Notebook widget inside the main_frame.The notebook is a tabbed widget to host multiple pages (tabs) for different content sections.
        self.notebook = ttk.Notebook(main_frame)
        # Packs the notebook into main_frame using the pack geometry manager.
        # fill="both" means it fills both horizontally and vertically.
        # expand=True allows it to grow and take up all available space inside the frame
        self.notebook.pack(fill="both", expand=True)

        # Creates a new frame tab_rooms which will be the content area for the "Rooms" tab inside the notebook.
        self.tab_rooms = ttk.Frame(self.notebook)
        # Adds the tab_rooms frame as a tab in the notebook with the label "Rooms".
        self.notebook.add(self.tab_rooms, text="Rooms")

        # Creates a new frame tab_res which will be the content area for the "Reservations" tab inside the notebook.
        self.tab_res = ttk.Frame(self.notebook)
        # Adds the tab_res frame as a tab in the notebook with the label "Reservations".
        self.notebook.add(self.tab_res, text="Reservations")

        # Calls methods to populate the "Rooms" tab and the "Reservations" tab with widgets and layout
        self.build_rooms_tab()
        self.build_reservations_tab()

    # ---------------- Rooms Tab ----------------
    def build_rooms_tab(self):
        # Assigns the "Rooms" tab to a local variable frame for easier reference.
        frame = self.tab_rooms
        # Creates a toolbar frame (top) inside the "Rooms" tab.
        # The toolbar stretches horizontally (fill="x") with vertical padding(main tab and the data table) (15 pixels).
        top = ttk.Frame(frame)
        top.pack(fill="x", pady=15)

        # Places buttons labeled "Add Room", "Edit Room","Remove Room","Refresh","Show Available Only" on the toolbar (left-aligned).
        # When clicked, calls self.[relevent function name] to open a mini dialog  box for each functionality.
        ttk.Button(top, text="Add Room", command=self.add_room_dialog).pack(side="left", padx=4)
        ttk.Button(top, text="Edit Room", command=self.edit_room_dialog).pack(side="left", padx=4)
        ttk.Button(top, text="Remove Room", command=self.remove_room).pack(side="left", padx=4)
        ttk.Button(top, text="Refresh", command=self.refresh_rooms).pack(side="left", padx=4)
        ttk.Button(top, text="Show Available Only", command=self.filter_available_rooms).pack(side="left", padx=4)

        # Datatable for rooms
        # Defines column names for the rooms table: Room number, type, price, and availability.
        cols = ("number", "type", "price", "available")
        # Creates a Treeview widget (tabular display) within the "Rooms" tab with these columns.
        # show="headings" means only the column headings and rows will be visible, not a tree hierarchy.​
        # selectmode="browse" allows only single row selection at a time.
        self.rooms_tv = ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")

        for c in cols:
            # For each column, sets its heading label (with the column name first letter capital by using .title() and centers the text in the column using anchor="center".
            self.rooms_tv.heading(c, text=c.title())
            self.rooms_tv.column(c, anchor="center")
        # Packs the treeview so it fills available space in both dimensions, with padding for spacing.
        self.rooms_tv.pack(fill="both", expand=True, padx=6, pady=6)
    
    # Add room dialog box
    def add_room_dialog(self):
        # Opens a modal dialog for entering new room info.
        dlg = RoomForm(self, title="Add Room")
        # Waits for user input.
        self.wait_window(dlg.top)
        # If the user submitted data (dlg.result), it extracts the values.
        if dlg.result:
            number, rtype, price = dlg.result
            try:
                # Tries to add a room using self.hotel.add_room().
                self.hotel.add_room(number, rtype, price)
                # Shows a success or error message accordingly.
                messagebox.showinfo("Success", f"Room {number} added.")
                # Refreshes the room list.
                self.refresh_rooms()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    # Edit room dialog box
    def edit_room_dialog(self):
        # Checks whether a room is selected; prompts user if not.
        sel = self.rooms_tv.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a room to edit.")
            return
        # retrieves the first selected item's ID from the tuple
        number = int(sel[0])
        # calls the get_room method in your storage object
        room = self.storage.get_room(number)
        if not room:
            messagebox.showerror("Error", "Room not found.")
            return
        # Loads the selected room's info and Opens a dialog (RoomForm) with pre-filled details.
        dlg = RoomForm(self, title="Edit Room", defaults=(room.number, room.room_type, room.price))
        self.wait_window(dlg.top)
        if dlg.result:
            number, rtype, price = dlg.result
            try:
                self.storage.update_room(number, rtype, price)
                messagebox.showinfo("Updated", "Room updated.")
                self.refresh_rooms()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # Remove room dialog box 
    def remove_room(self):
        sel = self.rooms_tv.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a room to remove.")
            return
        number = int(sel[0])
        try:
            self.hotel.remove_room(number)
            messagebox.showinfo("Removed", f"Room {number} removed.")
            self.refresh_rooms()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Refresh the rooms list after a room deletes 
    # The available_only parameter is a flag: if it's True, only available rooms will be shown
    def refresh_rooms(self, available_only=False):
        # Loops through all current rows/items (get_children()) in the Treeview displaying rooms.
        for i in self.rooms_tv.get_children():
            # Deletes them all, so the Treeview is emptied before being repopulated with up-to-date information.
            self.rooms_tv.delete(i)
        # Loads the full list of room records from the database by calling list_rooms()
        rooms = self.storage.list_rooms()
        # If showing only available rooms is requested, filters the rooms list to only include those where available is True.
        if available_only:
            rooms = [r for r in rooms if r.available]
        # For each Room instance in the (possibly filtered) rooms list:
        # Inserts a new row in the Treeview.
        # Sets the row's unique ID (iid) to be the room number (as a string).
        # Sets the cell values to display: room number, room type (as text), price (formatted to two decimals), and availability (as a string).
        # The first argument "" means no parent — the entry is at root level in flat tables.
        for r in rooms:
            self.rooms_tv.insert("", "end", iid=str(r.number), values=(r.number, r.room_type.value, f"{r.price:.2f}", str(r.available)))

    # Filter only the available rooms
    def filter_available_rooms(self):
        self.refresh_rooms(available_only=True)

    # ---------------- Reservations Tab ----------------
    def build_reservations_tab(self):
        # Assigns the "Reservation" tab to a local variable frame for easier reference.
        frame = self.tab_res
        # # Creates a toolbar frame (top) inside the "Rooms" tab.
        # The toolbar stretches horizontally (fill="x") with vertical padding(main tab and the data table) (15 pixels).
        top = ttk.Frame(frame)
        top.pack(fill="x", pady=15)

        # Places buttons labeled "Book Room", "Check-in","Check-out","Cancel","Refresh" on the toolbar (left-aligned).
        # When clicked, calls self.[relevent function name] to open a mini dialog  box for each functionality.
        ttk.Button(top, text="Book Room", command=self.book_room_dialog).pack(side="left", padx=4)
        ttk.Button(top, text="Check-in", command=self.checkin_dialog).pack(side="left", padx=4)
        ttk.Button(top, text="Check-out", command=self.checkout_dialog).pack(side="left", padx=4)
        ttk.Button(top, text="Cancel", command=self.cancel_reservation_dialog).pack(side="left", padx=4)
        ttk.Button(top, text="Refresh", command=self.refresh_reservations).pack(side="left", padx=4)

        # assign the datatable with column names
        cols = ("id", "room_number", "guest_name", "check_in", "check_out", "status")
        self.res_tv = ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            self.res_tv.heading(c, text=c.title())
            self.res_tv.column(c, anchor="center")
        self.res_tv.pack(fill="both", expand=True, padx=6, pady=6)

    # refresh the list with the booking status
    def refresh_reservations(self):
        for i in self.res_tv.get_children():
            self.res_tv.delete(i)
        for r in self.hotel.list_all_reservations():
            # For each reservation, inserts a new row (record) into the Treeview.
            # "" as the first parameter means it’s a top-level row in a flat table.
            # "end" means the new row is added at the end of the current table.
            # iid=str(r.id) sets the row's unique ID to the reservation's ID as a string.
            # The values parameter gives a tuple of what should appear in each column.
            self.res_tv.insert("", "end", iid=str(r.id), values=(r.id, r.room_number, r.guest_name, r.check_in or "-", r.check_out or "-", r.status.value))

    # Book a Room dialog box
    def book_room_dialog(self):
        dlg = BookForm(self, self.storage)
        self.wait_window(dlg.top)
        if dlg.result:
            room_num, guest_name, check_in, check_out = dlg.result
            try:
                res_id = self.hotel.book_room(room_num, guest_name, check_in, check_out)
                messagebox.showinfo("Booked", f"Reservation created (ID {res_id}).")
                self.refresh_reservations()
                self.refresh_rooms()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # Checkin a guest
    def checkin_dialog(self):
        sel = self.res_tv.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a reservation to check-in.")
            return
        rid = int(sel[0])
        try:
            self.hotel.check_in(rid)
            messagebox.showinfo("Checked-in", "Guest checked in.")
            self.refresh_reservations()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Checkout the guest
    def checkout_dialog(self):
        sel = self.res_tv.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a reservation to check-out.")
            return
        rid = int(sel[0])
        try:
            self.hotel.check_out(rid)
            messagebox.showinfo("Checked-out", "Guest checked out.")
            self.refresh_reservations()
            self.refresh_rooms()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Cancel a reservation
    def cancel_reservation_dialog(self):
        sel = self.res_tv.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a reservation to cancel.")
            return
        rid = int(sel[0])
        try:
            self.hotel.cancel_reservation(rid)
            messagebox.showinfo("Cancelled", "Reservation cancelled.")
            self.refresh_reservations()
            self.refresh_rooms()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- Utilities ----------------
    def show_tab(self, name):
        if name == "rooms":
            self.notebook.select(self.tab_rooms)
        elif name == "reservations":
            self.notebook.select(self.tab_res)

    def refresh_all(self):
        self.refresh_rooms()
        self.refresh_reservations()


# ---------- Dialogs & Forms ----------
class RoomForm:
    def __init__(self, parent, title="Room Form", defaults=None):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.result = None

        # styling mini dialog box for add Rooms while aligning labels 
        ttk.Label(self.top, text="Room number:").grid(row=0, column=0, sticky="w")
        self.e_number = ttk.Entry(self.top); self.e_number.grid(row=0, column=1, padx=25, pady=10)

        ttk.Label(self.top, text="Room type:").grid(row=1, column=0, sticky="w")
        self.type_cb = ttk.Combobox(self.top, values=[t.value for t in RoomType], state="readonly")
        self.type_cb.grid(row=1, column=1, pady=10)

        ttk.Label(self.top, text="Price:").grid(row=2, column=0, sticky="w")
        self.e_price = ttk.Entry(self.top); self.e_price.grid(row=2, column=1, pady=10)

        ttk.Button(self.top, text="OK", command=self.on_ok).grid(row=3, column=0, pady=8)
        ttk.Button(self.top, text="Cancel", command=self.top.destroy).grid(row=3, column=1, pady=8)

        if defaults:
            # Pre-fills the entries with existing values for room number, room type, and price.
            # Disables the room number field (state="disabled") to prevent editing—important for primary key integrity.
            # Sets dropdown/entry text appropriately.
            number, rtype, price = defaults
            self.e_number.insert(0, str(number))
            self.e_number.config(state="disabled")
            self.type_cb.set(rtype.value if isinstance(rtype, RoomType) else rtype.value)
            self.e_price.insert(0, str(price))

    def on_ok(self):
        # Reads the entries and dropdown values, cleans whitespace.
        # Converts input types appropriately (room number to int, price to float).
        # Converts the string dropdown selection to the RoomType Enum.
        # If all is valid: Sets self.result to a tuple of values and closes the dialog (the parent waits for dialog to close and retrieves result).
        # If error/invalid input: Shows a popup error message (user must correct input).
        try:
            number = int(self.e_number.get().strip())
            rtype = self.type_cb.get().strip()
            price = float(self.e_price.get().strip())
            rt_enum = RoomType(rtype)
            self.result = (number, rt_enum, price)
            self.top.destroy()
        except Exception as e:
            messagebox.showerror("Invalid", str(e))

class BookForm:
    def __init__(self, parent, storage: Storage):
        self.top = tk.Toplevel(parent)
        self.top.title("Book Room")
        self.result = None
        self.storage = storage

        # styling mini dialog box for Book a room 
        ttk.Label(self.top, text="Room number:").grid(row=0, column=0, sticky="w")
        self.e_room = ttk.Combobox(self.top, values=[r.number for r in storage.list_rooms()], state="readonly")
        self.e_room.grid(row=0, column=1, pady=10)

        ttk.Label(self.top, text="Guest name:").grid(row=1, column=0, sticky="w")
        self.e_guest = ttk.Entry(self.top); self.e_guest.grid(row=1, column=1, pady=10)

        ttk.Label(self.top, text="Check-in (YYYY-MM-DD):").grid(row=2, column=0, sticky="w")
        self.e_checkin = ttk.Entry(self.top); self.e_checkin.grid(row=2, column=1, pady=10)

        ttk.Label(self.top, text="Check-out (YYYY-MM-DD or blank):").grid(row=3, column=0, sticky="w")
        self.e_checkout = ttk.Entry(self.top); self.e_checkout.grid(row=3, column=1, pady=10)

        ttk.Button(self.top, text="Book", command=self.on_book).grid(row=4, column=0, pady=8)
        ttk.Button(self.top, text="Cancel", command=self.top.destroy).grid(row=4, column=1, pady=8)

    def on_book(self):
        try:
            # Fetches the room number from an Entry widget called self.e_room by converting to int
            room_num = int(self.e_room.get())
            # Fetches guest name and check-in date from Entry widgets, stripping any whitespace before or after the text.
            guest = self.e_guest.get().strip()
            check_in = self.e_checkin.get().strip()
            # Form-level validation: Checks that neither the guest name nor the check-in field is empty. if either is missing, raises a ValueError, which is handled by showing an error message.
            if not guest or not check_in:
                raise ValueError("Guest and check-in required.")
            # If the check-out field is not empty, tries to parse it using date.fromisoformat(). If not a valid YYYY-MM-DD string, raises a ValueError
            if self.e_checkout.get().strip():
                _ = date.fromisoformat(self.e_checkout.get().strip())
            _ = date.fromisoformat(check_in)
            # If all validations pass: Packs all the cleaned user inputs into a tuple and stores it as self.result
            self.result = (room_num, guest, check_in, self.e_checkout.get().strip() or None)
            self.top.destroy()
        except Exception as e:
            messagebox.showerror("Invalid", str(e))

# ------------- Run GUI -------------
def run_gui():
    # Create a storage object to handle interactions with the database.
    # Storage(db_path=DB_NAME) tries to construct a new Storage object, giving it the path to your database (likely a string like "hotel.db"
    storage = Storage(db_path=DB_NAME) if hasattr(Storage, "__init__") else Storage()
    # This object will handle hotel-specific logic (like checking room availability, making reservations, etc.) by using the storage layer
    hotel = Hotel(storage)
    #  Create the graphical user interface (GUI) for the hotel app.
    app = HotelGUI(storage, hotel)
    # Start the Tkinter main event loop
    app.mainloop()

if __name__ == "__main__":
    run_gui()
