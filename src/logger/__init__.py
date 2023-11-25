# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import os

from .logger import CustomLogger

_logger = None

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)


def get_logger() -> CustomLogger:
    global _logger
    if _logger is None:
        _logger = CustomLogger("AMOS-APP", dname + "/../../logs/")
    return _logger
