# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>


# Utility Functions
def get_yes_no_input(prompt: str) -> bool:
    """
    Prompts the user with a given prompt and returns True if the user enters 'yes' or 'y',
    and False if the user enters 'no' or 'n'. The input is case-insensitive.

    Args:
        prompt (str): The prompt to display to the user.

    Returns:
        bool: True if the user enters 'yes' or 'y', False if the user enters 'no' or 'n'.
    """
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ["y", "yes"]:
            return True
        elif user_input in ["n", "no"]:
            return False
        else:
            print("Invalid input. Please enter (yes/no) or (y/N).")


def get_int_input(prompt: str, input_range: range = None) -> int:
    """
    Prompts the user for an integer input and validates it.

    Args:
        prompt (str): The prompt message to display to the user.
        input_range (range, optional): The range of valid input values. Defaults to None.

    Returns:
        int: The validated integer input.

    Raises:
        ValueError: If the input is not a valid integer.

    """
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


def get_multiple_choice(prompt: str, choices: list) -> str:
    """
    Prompts the user with a message and a list of choices, and returns the selected choice.

    Args:
        prompt (str): The message to display to the user.
        choices (list): The list of choices to display to the user.

    Returns:
        str: The selected choice.

    Raises:
        ValueError: If the user enters an invalid input.
    """
    while True:
        try:
            prompt += "".join(
                f"({index}) : {choice} \n" for index, choice in enumerate(choices)
            )
            ind = get_int_input(prompt, range(len(choices) + 1))
            return choices[ind]
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
