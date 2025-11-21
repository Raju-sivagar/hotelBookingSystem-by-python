
# File Name: enums.py
# Description: enumeration classes for room types & reservation statuses used throughout the Hotel Booking System.
# Author: Dasuni senavirathna
# Date: 2025-11-21

from enum import Enum


class RoomType(Enum):
#Enumeration for the different types of hotel rooms.#
    SINGLE = "Single"
    DOUBLE = "Double"
    SUITE = "Suite"
    DELUXE = "Deluxe"


class ReservationStatus(Enum):
#Enumeration to track the status of a hotel reservation.#
    BOOKED = "Booked"
    CHECKED_IN = "Checked-in"
    CHECKED_OUT = "Checked-out"
    CANCELLED = "Cancelled"
