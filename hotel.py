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

    def add_room(self, number: int, room_type: RoomType, price: float): # Check if a room with this number already exists.
        room = self.storage.get_room(number) 
        if room:
            raise ValueError("Room already exists.")
        new_room = Room(number, room_type, price, True) # if room number already available, create new room
        self.storage.add_room(new_room)

    def view_available_rooms(self):
        return [r for r in self.storage.list_rooms() if r.available] #  Get all rooms from storage and return only the ones marked as available.

    def book_room(self, number, guest_name, check_in, check_out):
        room = self.storage.get_room(number) # get the room by its number
        if not room or not room.available: #  If the room doesn't exist or is not available, stop.
            raise ValueError("Room unavailable.")

        nights = 1
        if check_out: # Convert ISO date strings like "2025-11-24" to date objects.
            d1 = datetime.date.fromisoformat(check_in)
            d2 = datetime.date.fromisoformat(check_out)
            nights = (d2 - d1).days #  number of nights as the day differece (d2-d1)

        total = max(nights, 1) * room.price

        res = Reservation(None, number, guest_name,
                          check_in, check_out,
                          ReservationStatus.BOOKED, total)
    #  Create a Reservation object.
        # - id is None (storage will assign one)
        # - number is the room number
        # - guest_name is who is booking
        # - check_in/check_out are the dates
        # - status is BOOKED
        # - total is the total price for the stay
        
        new_id = self.storage.add_reservation(res) #  Save reservation and get its new ID from storage.
        self.storage.update_room_availability(number, False) #  # Mark the room as no longer available.
        return new_id

    def check_out(self, reservation_id: int): # Look up the reservation by ID.
        res = self.storage.get_reservation_by_id(reservation_id) #  If reservation does not exist, raise an error.
        if not res:
            raise ValueError("Reservation not found.")

        self.storage.update_reservation_status(   #  Update the reservation status to CHECKED_OUT and set the checkout date to today's date
            reservation_id,
            ReservationStatus.CHECKED_OUT.value,
            datetime.date.today().isoformat()
        )
        self.storage.update_room_availability(res.room_number, True) # Make the room available again for future bookings.

    def list_all_reservations(self):
        return self.storage.list_reservations()
