# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>


# Utility Functions
def get_yes_no_input(prompt: str) -> bool:
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ["y", "yes"]:
            return True
        elif user_input in ["n", "no"]:
            return False
        else:
            print("Invalid input. Please enter (yes/no) or (y/N).")


def get_int_input(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
