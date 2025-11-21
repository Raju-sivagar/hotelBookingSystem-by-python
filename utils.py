# # File Name: utils.py
# Description:  helper functions (safe_input, validators, etc)

# Author: Dasuni senavirathna
# Date: 2025-11-21

def safe_input(prompt, cast=str, allow_empty=False):
    while True:
        try:
            val = input(prompt).strip()
            if not val and not allow_empty:
                print("Input cannot be empty.")
                continue
            return cast(val) if cast != str else val
        except ValueError:
            print("Invalid input type.")
