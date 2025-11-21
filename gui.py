# gui.py
"""
Tkinter Dashboard (Full) for Hotel Booking System - Option C
Features:
 - Sidebar navigation
 - Tabbed interface: Rooms, Reservations, Reports
 - Treeview tables for rooms & reservations
 - Add/Edit/Delete rooms, Book, Check-in, Check-out, Cancel
 - CSV export buttons
 - Uses Hotel, Storage, Enums modules for business logic/persistence
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import date
import csv
import os

# Import your modules (assumes same folder)
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

        # ====== Colorful Theme Setup ======
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#E7F6F2")
        style.configure("TLabel", background="#E7F6F2", foreground="#125B50", font=("Segoe UI", 12, "bold"))
        style.configure("TButton", background="#0B8F3E", foreground="white", font=("Segoe UI", 11))
        style.map("TButton",
                  background=[("active", "#25A18E"), ("pressed", "#F58634")],
                  foreground=[("disabled", "#ccc")])
        style.configure("Sidebar.TFrame", background="#F58634")
        style.configure("Sidebar.TLabel", background="#F58634", foreground="#fff", font=("Segoe UI", 14, "bold"))
        style.configure("Sidebar.TButton", background="#FFB703", foreground="#023E8A", font=("Segoe UI", 11, "bold"))
        style.map("Sidebar.TButton",
                  background=[('active', "#FFFBEA"), ('pressed', "#8AC6D1")])
        style.configure("TNotebook", background="#CFFDE1", borderwidth=0)
        style.configure("TNotebook.Tab", background="#25A18E", foreground="white", font=("Segoe UI", 11, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", "#F58634"), ("active", "#F6E7D8")],
                  foreground=[("selected", "#fff"), ("active", "#125B50")])
        style.configure("Treeview", background="#B6E2D3", foreground="#125B50", fieldbackground="#DFFFDE", font=("Segoe UI", 10))
        style.map("Treeview", background=[("selected", "#25A18E")])

        self.create_widgets()
        self.refresh_all()

    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar frame
        sidebar = ttk.Frame(self, width=200, padding=(8, 8), style="Sidebar.TFrame")
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        ttk.Label(sidebar, text="Menu", style="Sidebar.TLabel").pack(pady=(0,10))
        ttk.Button(sidebar, text="Rooms", style="Sidebar.TButton", command=lambda: self.show_tab("rooms")).pack(fill="x", pady=4)
        ttk.Button(sidebar, text="Reservations", style="Sidebar.TButton", command=lambda: self.show_tab("reservations")).pack(fill="x", pady=4)
        ttk.Button(sidebar, text="Reports", style="Sidebar.TButton", command=lambda: self.show_tab("reports")).pack(fill="x", pady=4)
        ttk.Separator(sidebar).pack(fill="x", pady=8)
        ttk.Button(sidebar, text="Add Sample Data", style="Sidebar.TButton", command=self.add_sample_data).pack(fill="x", pady=4)
        ttk.Button(sidebar, text="Export CSVs", style="Sidebar.TButton", command=self.export_all_csvs).pack(fill="x", pady=4)
        ttk.Button(sidebar, text="Quit", style="Sidebar.TButton", command=self.quit).pack(fill="x", pady=(30,4))

        # Main area with Notebook
        main_frame = ttk.Frame(self, padding=(8,8))
        main_frame.grid(row=0, column=1, sticky="nsew")

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        # Rooms tab
        self.tab_rooms = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_rooms, text="Rooms")

        # Reservations tab
        self.tab_res = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_res, text="Reservations")

        # Reports tab
        self.tab_reports = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_reports, text="Reports")

        self.build_rooms_tab()
        self.build_reservations_tab()
        self.build_reports_tab()

    # ---------------- Rooms Tab ----------------
    def build_rooms_tab(self):
        frame = self.tab_rooms
        top = ttk.Frame(frame)
        top.pack(fill="x", pady=6)

        ttk.Button(top, text="Add Room", command=self.add_room_dialog).pack(side="left", padx=4)
        ttk.Button(top, text="Edit Room", command=self.edit_room_dialog).pack(side="left", padx=4)
        ttk.Button(top, text="Remove Room", command=self.remove_room).pack(side="left", padx=4)
        ttk.Button(top, text="Refresh", command=self.refresh_rooms).pack(side="left", padx=4)
        ttk.Button(top, text="Show Available Only", command=self.filter_available_rooms).pack(side="left", padx=4)

        # Treeview for rooms
        cols = ("number", "type", "price", "available")
        self.rooms_tv = ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            self.rooms_tv.heading(c, text=c.title())
            self.rooms_tv.column(c, anchor="center")
        self.rooms_tv.pack(fill="both", expand=True, padx=6, pady=6)

    def refresh_rooms(self, available_only=False):
        for i in self.rooms_tv.get_children():
            self.rooms_tv.delete(i)
        rooms = self.storage.list_rooms()
        if available_only:
            rooms = [r for r in rooms if r.available]
        for r in rooms:
            self.rooms_tv.insert("", "end", iid=str(r.number), values=(r.number, r.room_type.value, f"{r.price:.2f}", str(r.available)))

    def add_room_dialog(self):
        dlg = RoomForm(self, title="Add Room")
        self.wait_window(dlg.top)
        if dlg.result:
            number, rtype, price = dlg.result
            try:
                self.hotel.add_room(number, rtype, price)
                messagebox.showinfo("Success", f"Room {number} added.")
                self.refresh_rooms()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def edit_room_dialog(self):
        sel = self.rooms_tv.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a room to edit.")
            return
        number = int(sel[0])
        room = self.storage.get_room(number)
        if not room:
            messagebox.showerror("Error", "Room not found.")
            return
        dlg = RoomForm(self, title="Edit Room", defaults=(room.number, room.room_type, room.price))
        self.wait_window(dlg.top)
        if dlg.result:
            number_new, rtype, price = dlg.result
            try:
                self.storage.delete_room(number)
                self.hotel.add_room(number_new, rtype.value if isinstance(rtype, RoomType) else rtype.value, price)
                messagebox.showinfo("Updated", "Room updated.")
                self.refresh_rooms()
            except Exception as e:
                messagebox.showerror("Error", str(e))

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

    def filter_available_rooms(self):
        self.refresh_rooms(available_only=True)

    # ---------------- Reservations Tab ----------------
    def build_reservations_tab(self):
        frame = self.tab_res
        top = ttk.Frame(frame)
        top.pack(fill="x", pady=6)

        ttk.Button(top, text="Book Room", command=self.book_room_dialog).pack(side="left", padx=4)
        ttk.Button(top, text="Check-in", command=self.checkin_dialog).pack(side="left", padx=4)
        ttk.Button(top, text="Check-out", command=self.checkout_dialog).pack(side="left", padx=4)
        ttk.Button(top, text="Cancel", command=self.cancel_reservation_dialog).pack(side="left", padx=4)
        ttk.Button(top, text="Refresh", command=self.refresh_reservations).pack(side="left", padx=4)

        cols = ("id", "room_number", "guest_name", "check_in", "check_out", "status", "total")
        self.res_tv = ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            self.res_tv.heading(c, text=c.title())
            self.res_tv.column(c, anchor="center")
        self.res_tv.pack(fill="both", expand=True, padx=6, pady=6)

    def refresh_reservations(self):
        for i in self.res_tv.get_children():
            self.res_tv.delete(i)
        for r in self.hotel.list_all_reservations():
            self.res_tv.insert("", "end", iid=str(r.id), values=(r.id, r.room_number, r.guest_name, r.check_in or "-", r.check_out or "-", r.status.value, f"{r.total_price:.2f}"))

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

    # ---------------- Reports Tab ----------------
    def build_reports_tab(self):
        frame = self.tab_reports
        ttk.Label(frame, text="Reports and Exports", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(6,12), padx=8)
        ttk.Button(frame, text="Export Rooms CSV", command=self.export_rooms_csv).pack(anchor="w", padx=8, pady=4)
        ttk.Button(frame, text="Export Reservations CSV", command=self.export_reservations_csv).pack(anchor="w", padx=8, pady=4)
        ttk.Button(frame, text="Open exported files folder", command=self.open_exports_folder).pack(anchor="w", padx=8, pady=4)

        self.stats_box = tk.Text(frame, height=10, state="disabled")
        self.stats_box.pack(fill="both", expand=True, padx=8, pady=8)

    def export_rooms_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")], initialfile="rooms_export.csv")
        if not path:
            return
        self.hotel.export_rooms_csv(path)
        messagebox.showinfo("Exported", f"Rooms exported to {path}")

    def export_reservations_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")], initialfile="reservations_export.csv")
        if not path:
            return
        self.hotel.export_reservations_csv(path)
        messagebox.showinfo("Exported", f"Reservations exported to {path}")

    def open_exports_folder(self):
        folder = os.getcwd()
        messagebox.showinfo("Folder", f"Files are in: {folder}")

    def export_all_csvs(self):
        r1 = self.hotel.export_rooms_csv("rooms_export.csv")
        r2 = self.hotel.export_reservations_csv("reservations_export.csv")
        messagebox.showinfo("Exported", f"Rooms -> {r1}\nReservations -> {r2}")

    # ---------------- Utilities ----------------
    def show_tab(self, name):
        if name == "rooms":
            self.notebook.select(self.tab_rooms)
        elif name == "reservations":
            self.notebook.select(self.tab_res)
        elif name == "reports":
            self.notebook.select(self.tab_reports)

    def refresh_all(self):
        self.refresh_rooms()
        self.refresh_reservations()
        self.update_stats()

    def update_stats(self):
        total_rooms = len(self.storage.list_rooms())
        available = len([r for r in self.storage.list_rooms() if r.available])
        total_res = len(self.hotel.list_all_reservations())
        checked_in = len([r for r in self.hotel.list_all_reservations() if r.status == ReservationStatus.CHECKED_IN])
        txt = (
            f"Total rooms: {total_rooms}\n"
            f"Available rooms: {available}\n"
            f"Total reservations: {total_res}\n"
            f"Currently checked-in: {checked_in}\n"
            f"Date: {date.today().isoformat()}\n"
        )
        self.stats_box.config(state="normal")
        self.stats_box.delete("1.0", tk.END)
        self.stats_box.insert(tk.END, txt)
        self.stats_box.config(state="disabled")

    def add_sample_data(self):
        try:
            if not self.storage.list_rooms():
                self.hotel.add_room(101, RoomType.SINGLE.value, 50.0)
                self.hotel.add_room(102, RoomType.DOUBLE.value, 80.0)
                self.hotel.add_room(201, RoomType.SUITE.value, 150.0)
                messagebox.showinfo("Sample Data", "Sample rooms added.")
                self.refresh_all()
            else:
                messagebox.showinfo("Info", "Rooms already exist; no sample data added.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# ---------- Dialogs & Forms ----------
class RoomForm:
    def __init__(self, parent, title="Room Form", defaults=None):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.result = None

        ttk.Label(self.top, text="Room number:").grid(row=0, column=0, sticky="e")
        self.e_number = ttk.Entry(self.top); self.e_number.grid(row=0, column=1, pady=4)

        ttk.Label(self.top, text="Room type:").grid(row=1, column=0, sticky="e")
        self.type_cb = ttk.Combobox(self.top, values=[t.value for t in RoomType], state="readonly")
        self.type_cb.grid(row=1, column=1, pady=4)

        ttk.Label(self.top, text="Price:").grid(row=2, column=0, sticky="e")
        self.e_price = ttk.Entry(self.top); self.e_price.grid(row=2, column=1, pady=4)

        ttk.Button(self.top, text="OK", command=self.on_ok).grid(row=3, column=0, pady=8)
        ttk.Button(self.top, text="Cancel", command=self.top.destroy).grid(row=3, column=1, pady=8)

        if defaults:
            number, rtype, price = defaults
            self.e_number.insert(0, str(number))
            self.type_cb.set(rtype.value if isinstance(rtype, RoomType) else rtype.value)
            self.e_price.insert(0, str(price))

    def on_ok(self):
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

        ttk.Label(self.top, text="Room number:").grid(row=0, column=0, sticky="e")
        self.e_room = ttk.Combobox(self.top, values=[r.number for r in storage.list_rooms()], state="readonly")
        self.e_room.grid(row=0, column=1, pady=4)

        ttk.Label(self.top, text="Guest name:").grid(row=1, column=0, sticky="e")
        self.e_guest = ttk.Entry(self.top); self.e_guest.grid(row=1, column=1, pady=4)

        ttk.Label(self.top, text="Check-in (YYYY-MM-DD):").grid(row=2, column=0, sticky="e")
        self.e_checkin = ttk.Entry(self.top); self.e_checkin.grid(row=2, column=1, pady=4)

        ttk.Label(self.top, text="Check-out (YYYY-MM-DD or blank):").grid(row=3, column=0, sticky="e")
        self.e_checkout = ttk.Entry(self.top); self.e_checkout.grid(row=3, column=1, pady=4)

        ttk.Button(self.top, text="Book", command=self.on_book).grid(row=4, column=0, pady=8)
        ttk.Button(self.top, text="Cancel", command=self.top.destroy).grid(row=4, column=1, pady=8)

    def on_book(self):
        try:
            room_num = int(self.e_room.get())
            guest = self.e_guest.get().strip()
            check_in = self.e_checkin.get().strip()
            if not guest or not check_in:
                raise ValueError("Guest and check-in required.")
            # Validate dates (simple)
            if self.e_checkout.get().strip():
                _ = date.fromisoformat(self.e_checkout.get().strip())
            _ = date.fromisoformat(check_in)
            self.result = (room_num, guest, check_in, self.e_checkout.get().strip() or None)
            self.top.destroy()
        except Exception as e:
            messagebox.showerror("Invalid", str(e))

# ------------- Run GUI -------------
def run_gui():
    storage = Storage(db_path=DB_NAME) if hasattr(Storage, "__init__") else Storage()
    hotel = Hotel(storage)
    app = HotelGUI(storage, hotel)
    app.mainloop()

if __name__ == "__main__":
    run_gui()
