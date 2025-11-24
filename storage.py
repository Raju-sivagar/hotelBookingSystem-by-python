
# File Name: storage.py
# Description: Handles the database operations relevant to each functionality.
# Author: Piyumi Ediriweera
# Date: 2025-11-21


import sqlite3
import contextlib
from typing import Optional, List
from models import Room, Reservation
from enums import RoomType, ReservationStatus

DB_PATH = "hotel.db"
class Storage:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    # Database connection helper
    @contextlib.contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=5)
        try:
            yield conn
        finally:
            conn.close()

    
    # Create tables if they don't exist
    def _init_db(self):
        with self._connect() as conn:
            c = conn.cursor()

            c.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    number INTEGER PRIMARY KEY,
                    type TEXT NOT NULL,
                    price REAL NOT NULL,
                    available INTEGER NOT NULL
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_number INTEGER NOT NULL,
                    guest_name TEXT NOT NULL,
                    check_in TEXT NOT NULL,
                    check_out TEXT,
                    status TEXT NOT NULL
                )
            """)

            conn.commit()

    # ROOM OPERATIONS
    # Add rooms
    def add_room(self, room: Room):
        with self._connect() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO rooms VALUES (?, ?, ?, ?)",
                (room.number, room.room_type.value, room.price, int(room.available))
            )
            conn.commit()

    # delete rooms
    def delete_room(self, number: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM rooms WHERE number=?", (number,))
            conn.commit()

    # update the room availability
    def update_room_availability(self, number: int, available: bool):
        with self._connect() as conn:
            conn.execute(
                "UPDATE rooms SET available=? WHERE number=?",
                (int(available), number)
            )
            conn.commit()
    
    # Update room
    def update_room(self, number: int, r_type: RoomType, price: float):
        with self._connect() as conn:
            conn.execute(
                "UPDATE rooms SET type=?, price=? WHERE number=?",
                (r_type.value, price, number)
            )
            conn.commit()

    # propt the rooms data according to the selected room to edit
    def get_room(self, number: int) -> Optional[Room]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM rooms WHERE number=?", (number,)
            ).fetchone()

            if row:
                return Room(
                    number=row[0],
                    room_type=RoomType(row[1]),
                    price=row[2],
                    available=bool(row[3])
                )
            return None

    # list all the rooms after adding ,delete etc
    def list_rooms(self) -> List[Room]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM rooms ORDER BY number"
            ).fetchall()

            return [
                Room(
                    number=r[0],
                    room_type=RoomType(r[1]),
                    price=r[2],
                    available=bool(r[3])
                )
                for r in rows
            ]

    
    # RESERVATION OPERATIONS
    # Add reservation
    def add_reservation(self, res: Reservation) -> int:
        with self._connect() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO reservations
                (room_number, guest_name, check_in, check_out, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                res.room_number,
                res.guest_name,
                res.check_in,
                res.check_out,
                res.status.value
            ))

            conn.commit()
            return c.lastrowid


    # find the reserved room to checkout the guest
    def get_reservation_by_id(self, res_id: int) -> Optional[Reservation]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM reservations WHERE id=?", (res_id,)
            ).fetchone()

            if row:
                return Reservation(
                    id=row[0],
                    room_number=row[1],
                    guest_name=row[2],
                    check_in=row[3],
                    check_out=row[4],
                    status=ReservationStatus(row[5])
                )
            return None
    # update the reservation status after guest checked out 
    def update_reservation_status(self, res_id: int, status: str, check_out: str = None):
        with self._connect() as conn:
            conn.execute("""
                UPDATE reservations
                SET status=?, check_out=?
                WHERE id=?
            """, (status, check_out, res_id))
            conn.commit()
    
    # provide the list of the reservations
    def list_reservations(self) -> List[Reservation]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM reservations ORDER BY id").fetchall()
            return [
                Reservation(
                    id=r[0],
                    room_number=r[1],
                    guest_name=r[2],
                    check_in=r[3],
                    check_out=r[4],
                    status=ReservationStatus(r[5])
                )
                for r in rows
            ]
