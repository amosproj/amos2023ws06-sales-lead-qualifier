# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 Felix Zailskas <felixzailskas@gmail.com>

import unittest
from unittest import mock

from demo.console_utils import (
    get_int_input,
    get_multiple_choice,
    get_string_input,
    get_yes_no_input,
)


class TestGetYesNoInput(unittest.TestCase):
    @mock.patch("builtins.input", return_value="y")
    def test_input_y(self, mock_input):
        self.assertTrue(get_yes_no_input("Enter yes or no:"))
        mock_input.assert_called_with("Enter yes or no:")

    @mock.patch("builtins.input", return_value="yes")
    def test_input_yes(self, mock_input):
        self.assertTrue(get_yes_no_input("Enter yes or no:"))
        mock_input.assert_called_with("Enter yes or no:")

    @mock.patch("builtins.input", return_value="Y")
    def test_input_Y(self, mock_input):
        self.assertTrue(get_yes_no_input("Enter yes or no:"))
        mock_input.assert_called_with("Enter yes or no:")

    @mock.patch("builtins.input", return_value="YES")
    def test_input_YES(self, mock_input):
        self.assertTrue(get_yes_no_input("Enter yes or no:"))
        mock_input.assert_called_with("Enter yes or no:")

    @mock.patch("builtins.input", return_value="n")
    def test_input_n(self, mock_input):
        self.assertFalse(get_yes_no_input("Enter yes or no:"))
        mock_input.assert_called_with("Enter yes or no:")

    @mock.patch("builtins.input", return_value="no")
    def test_input_no(self, mock_input):
        self.assertFalse(get_yes_no_input("Enter yes or no:"))
        mock_input.assert_called_with("Enter yes or no:")

    @mock.patch("builtins.input", return_value="N")
    def test_input_N(self, mock_input):
        self.assertFalse(get_yes_no_input("Enter yes or no:"))
        mock_input.assert_called_with("Enter yes or no:")

    @mock.patch("builtins.input", return_value="NO")
    def test_input_NO(self, mock_input):
        self.assertFalse(get_yes_no_input("Enter yes or no:"))
        mock_input.assert_called_with("Enter yes or no:")

    @mock.patch("builtins.input", side_effect=["invalid", "y"])
    @mock.patch("builtins.print")
    def test_get_yes_no_input_invalid_input(self, mock_print, mock_input):
        result = get_yes_no_input("Enter yes or no: ")
        mock_input.assert_called_with("Enter yes or no: ")
        mock_print.assert_called_with("Invalid input. Please enter (yes/no) or (y/N).")
        self.assertTrue(result)


class TestGetStringInput(unittest.TestCase):
    @mock.patch("builtins.input", return_value="test")
    def test_valid_input(self, mock_input):
        result = get_string_input("Enter a string: ")
        self.assertEqual(result, "test")
        mock_input.assert_called_with("Enter a string: ")

    @mock.patch("builtins.input", side_effect=["", "   ", "valid_input"])
    def test_empty_input_then_valid_input(self, mock_input):
        result = get_string_input("Enter a string: ")
        self.assertEqual(result, "valid_input")
        mock_input.assert_has_calls(
            [
                mock.call("Enter a string: "),
                mock.call("Enter a string: "),
                mock.call("Enter a string: "),
            ]
        )


class TestGetIntInput(unittest.TestCase):
    @mock.patch("builtins.input", return_value="42")
    def test_valid_input(self, mock_input):
        result = get_int_input("Enter an integer: ")
        self.assertEqual(result, 42)
        mock_input.assert_called_with("Enter an integer: ")

    @mock.patch("builtins.input", side_effect=["invalid", "12"])
    def test_invalid_input_then_valid_input(self, mock_input):
        result = get_int_input("Enter an integer: ")
        self.assertEqual(result, 12)
        mock_input.assert_has_calls(
            [mock.call("Enter an integer: "), mock.call("Enter an integer: ")]
        )

    @mock.patch("builtins.input", side_effect=["7", "3"])
    def test_input_range(self, mock_input):
        result = get_int_input("Enter an integer: ", input_range=range(1, 5))
        self.assertEqual(result, 3)
        mock_input.assert_has_calls(
            [mock.call("Enter an integer: "), mock.call("Enter an integer: ")]
        )

    @mock.patch("builtins.input", side_effect=["invalid", "4"])
    def test_input_range_invalid_then_valid(self, mock_input):
        result = get_int_input("Enter an integer: ", input_range=range(1, 5))
        self.assertEqual(result, 4)
        mock_input.assert_has_calls(
            [mock.call("Enter an integer: "), mock.call("Enter an integer: ")]
        )


class TestGetMultipleChoice(unittest.TestCase):
    @mock.patch("demo.console_utils.get_int_input", return_value=0)
    def test_valid_input(self, mock_get_int_input):
        choices = ["Option A", "Option B", "Option C"]
        choice_string = "".join(
            f"({index}) : {choice} \n" for index, choice in enumerate(choices)
        )
        result = get_multiple_choice("Select an option: ", choices)
        self.assertEqual(result, "Option A")
        mock_get_int_input.assert_called_with(
            "Select an option: " + choice_string, range(len(choices))
        )


if __name__ == "__main__":
    unittest.main()
