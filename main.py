# # File Name: main.py
# Description:  launcher (CLI or GUI)
# Author: Raju Veeriah Sivagar, Piyumi Ediriwera, and Dasuni senavirathna
# Date: 2025-11-21

# main.py
import sys
import tkinter as tk
from utils import safe_input

# prefer CLI import only if needed
from storage import Storage
from hotel import Hotel

def run_cli():
    from main_cli import menu  # if you separated your CLI into main_cli.py
    menu()

def run_gui():
    import gui
    gui.run_gui()

if __name__ == "__main__":
    print("1) Run Console (CLI)")
    print("2) Run GUI (Tkinter Dashboard - Option C)")
    choice = input("Choose 1 or 2 (default 2): ").strip() or "2"
    if choice == "1":
        try:
            run_cli()
        except Exception as e:
            print("CLI start error:", e)
    else:
        run_gui()
