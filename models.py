
# File Name: models.py
# Description:  Defines the data models (Room and Reservation).  
#               These models structure the core data and 
#               stored and processed by the application.
#Author: Raju Veeriah Sivagar
#Date: 2025-11-21


from dataclasses import dataclass
from typing import Optional
from enums import RoomType, ReservationStatus


@dataclass
class Room:
    """
    Represents a hotel room.
    Attributes:
        number (int): Room number.
        room_type (RoomType): Type of the room (Single, Double, etc.).
        price (float): Cost per night.
        available (bool): Availability status.
    """
    number: int
    room_type: RoomType
    price: float
    available: bool = True


@dataclass
class Reservation:
    """
    Represents a hotel room reservation.
    Attributes:
        id (int): Unique reservation ID (None before saving to database).
        room_number (int): The room being reserved.
        guest_name (str): Guest full name.
        check_in (str): Check-in date (YYYY-MM-DD).
        check_out (str): Check-out date (YYYY-MM-DD or None).
        status (ReservationStatus): Status of the reservation.
        total_price (float): Calculated total cost of stay.
    """
    id: Optional[int]
    room_number: int
    guest_name: str
    check_in: str
    check_out: Optional[str]
    status: ReservationStatus
    total_price: float
