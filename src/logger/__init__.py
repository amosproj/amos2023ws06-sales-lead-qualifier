# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from .logger import CustomLogger

_logger = None


def get_logger() -> CustomLogger:
    global _logger
    if _logger is None:
        _logger = CustomLogger("AMOS-APP", "../logs/")
    return _logger
