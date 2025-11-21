# File Name: hotel.py
# Description:  business logic (Hotel class)

# Author: Raju Veeriah Sivagar
# Date: 2025-11-21

import datetime
from storage import Storage
from models import Room, Reservation
from enums import RoomType, ReservationStatus

class Hotel:
    def __init__(self, storage: Storage):
        self.storage = storage

    def add_room(self, number: int, room_type: RoomType, price: float):
        room = self.storage.get_room(number)
        if room:
            raise ValueError("Room already exists.")
        new_room = Room(number, room_type, price, True)
        self.storage.add_room(new_room)

    def view_available_rooms(self):
        return [r for r in self.storage.list_rooms() if r.available]

    def book_room(self, number, guest_name, check_in, check_out):
        room = self.storage.get_room(number)
        if not room or not room.available:
            raise ValueError("Room unavailable.")

        nights = 1
        if check_out:
            d1 = datetime.date.fromisoformat(check_in)
            d2 = datetime.date.fromisoformat(check_out)
            nights = (d2 - d1).days

        total = max(nights, 1) * room.price

        res = Reservation(None, number, guest_name,
                          check_in, check_out,
                          ReservationStatus.BOOKED, total)

        new_id = self.storage.add_reservation(res)
        self.storage.update_room_availability(number, False)
        return new_id

    def check_out(self, reservation_id: int):
        res = self.storage.get_reservation_by_id(reservation_id)
        if not res:
            raise ValueError("Reservation not found.")

        self.storage.update_reservation_status(
            reservation_id,
            ReservationStatus.CHECKED_OUT.value,
            datetime.date.today().isoformat()
        )
        self.storage.update_room_availability(res.room_number, True)

    def list_all_reservations(self):
        return self.storage.list_reservations()