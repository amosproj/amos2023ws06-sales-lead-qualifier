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


def get_int_input(prompt: str, input_range: range = None) -> int:
    while True:
        try:
            input_int = int(input(prompt))
            if input_range is not None and input_int not in input_range:
                print("Invalid input. Please enter a valid integer.")
                continue
            else:
                return input_int
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
