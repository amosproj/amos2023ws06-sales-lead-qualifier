# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

from threading import Lock
from typing import Any


class ControllerMeta(type):

    """
    Thread safe singleton implementation of Controller
    """

    _instances = {}
    _lock: Lock = Lock()

    def __call__(self, *args: Any, **kwds: Any):
        with self._lock:
            if self not in self._instances:
                instance = super().__call__(*args, **kwds)
                self._instances[self] = instance

        return self._instances[self]


class Controller(metaclass=ControllerMeta):
    def __init__(self, name: str) -> None:
        self.name = name
