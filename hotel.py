# File Name: hotel.py
# Description:  business logic (Hotel class)
# Author: Raju Veeriah Sivagar
# Date: 2025-11-21

import datetime
from storage import Storage
from models import Room, Reservation
from enums import RoomType, ReservationStatus

class Hotel:
    def __init__(self, storage: Storage):  # Saves the storage method we'll use for all hotel data
        self.storage = storage

    def add_room(self, number: int, room_type: RoomType, price: float): # Check if a room with this number already exists
        room = self.storage.get_room(number)
        if room:
            raise ValueError("Room already exists.")     # If it does, stop and show an error!
        new_room = Room(number, room_type, price, True)  # Make a new Room object, set as available (True)
        self.storage.add_room(new_room)                  # Add the new room to our data storage

    def view_available_rooms(self):                       # Get all rooms, only keep those marked available
        return [r for r in self.storage.list_rooms() if r.available]

    def book_room(self, number, guest_name, check_in, check_out):
        room = self.storage.get_room(number)              # Find the room by its number
        if not room or not room.available:
            raise ValueError("Room unavailable.")          # Stop if room doesn’t exist or isn’t available

        nights = 1                                           # Default to 1 night if not given
        if check_out:
            d1 = datetime.date.fromisoformat(check_in)        # Turn check-in date (string) into a date object
            d2 = datetime.date.fromisoformat(check_out)       # Turn check-out date (string) into a date object
            nights = (d2 - d1).days                           # Calculate how many nights between check-in and check-out

        total = max(nights, 1) * room.price

        res = Reservation(None, number, guest_name,
                          check_in, check_out,
                          ReservationStatus.BOOKED, total)    # Make a new reservation object

        new_id = self.storage.add_reservation(res)             # Save the reservation and get its unique ID
        self.storage.update_room_availability(number, False)
        return new_id                                           # Return the reservation’s ID (could be used to look up later)

    def check_out(self, reservation_id: int):
        res = self.storage.get_reservation_by_id(reservation_id)    # Mark room as unavailable, it’s now booked
        if not res:
            raise ValueError("Reservation not found.")                # If can’t find, stop with an error

        self.storage.update_reservation_status(
            reservation_id,
            ReservationStatus.CHECKED_OUT.value,                # Set status to “checked out”
            datetime.date.today().isoformat()                   # Use today for the actual check-out date
        )
        self.storage.update_room_availability(res.room_number, True)  # Mark the room as free again

    def list_all_reservations(self):
        return self.storage.list_reservations()  # Just get and return all reservations from storage
