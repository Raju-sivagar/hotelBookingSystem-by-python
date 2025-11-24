
# File Name: models.py
# Description:  Defines the data models (Room and Reservation).  
#               These models structure the core data and 
#               stored and processed by the application.
#Author: Raju Veeriah Sivagar
#Date: 2025-11-21


from dataclasses import dataclass                    #  Imports dataclass decorator to simplify class definitions.
from typing import Optional                          #  Imports Optional type hint for fields that can be None.
from enums import RoomType, ReservationStatus        # Imports enums for room type and reservation status.


# Represents a hotel room Attributes such as room number, room type, price per night, availability 
@dataclass                            # instruct Python to auto-generate common methods for this class.
class Room:
    
    number: int                  # room number 
    room_type: RoomType          # Room Type :singal, double, suite, deluxe 
    price: float                 # price per night 
    available: bool = True       # room availabilty set to default as ture bool value


@dataclass
class Reservation:
#Represents a hotel room reservation Attributes: ID, room number, guest name, check in & check out, satus, total cost of stay


    id: int
    room_number: int   # the room being reserved
    guest_name: str    # Guest full name
    check_in: str      # check in date (YYYY-MM-DD)
    check_out: str     # check out date (YYYY-MM-DD)
    status: ReservationStatus    # Status of reservation
    total_price: float    # calculated total cost of stay
