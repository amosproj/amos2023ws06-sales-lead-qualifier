# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

# source: https://alexandra-zaharia.github.io/posts/custom-logger-in-python-for-stdout-and-or-file-log/

import datetime
import logging
import os
import sys


class StdOutFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    blue = "\033[34m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    fmt = "%(asctime)s | %(levelname)8s | %(filename)s:%(lineno)d | %(message)s"

    FORMATS = {
        logging.DEBUG: grey + fmt + reset,
        logging.INFO: blue + fmt + reset,
        logging.WARNING: yellow + fmt + reset,
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: bold_red + fmt + reset,
    }

    def __init__(self):
        logging.Formatter.__init__(self, self.fmt)

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class FileOutFormatter(logging.Formatter):
    fmt = "%(asctime)s | %(levelname)8s | %(filename)s:%(lineno)d | %(message)s"

    def __init__(self):
        logging.Formatter.__init__(self, self.fmt)

    def format(self, record):
        formatter = logging.Formatter(self.fmt)
        return formatter.format(record)


class CustomLogger(logging.getLoggerClass()):
    def __init__(self, name, log_dir=None):
        # Create custom logger logging all five levels
        super().__init__(name)
        self.setLevel(logging.DEBUG)

        # Create stream handler for logging to stdout (log all five levels)
        self.stdout_handler = logging.StreamHandler(sys.stdout)
        self.stdout_handler.setLevel(logging.INFO)
        self.stdout_handler.setFormatter(StdOutFormatter())
        self.enable_console_output()

        # Add file handler only if the log directory was specified
        self.file_handler = None
        if log_dir:
            self.add_file_handler(name, log_dir)

    def add_file_handler(self, name, log_dir):
        """Add a file handler for this logger with the specified `name` (and
        store the log file under `log_dir`)."""

        # Determine log path/file name; create log_dir if necessary
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_name = f'{str(name).replace(" ", "_")}_{now}'
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                print(
                    "{}: Cannot create directory {}. ".format(
                        self.__class__.__name__, log_dir
                    ),
                    end="",
                    file=sys.stderr,
                )
                log_dir = "/tmp" if sys.platform.startswith("linux") else "."
                print(f"Defaulting to {log_dir}.", file=sys.stderr)

        log_file = os.path.join(log_dir, log_name) + ".log"

        # Create file handler for logging to a file (log all five levels)
        self.file_handler = logging.FileHandler(log_file)
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(FileOutFormatter())
        self.addHandler(self.file_handler)

    def has_console_handler(self):
        return len([h for h in self.handlers if type(h) == logging.StreamHandler]) > 0

    def has_file_handler(self):
        return len([h for h in self.handlers if isinstance(h, logging.FileHandler)]) > 0

    def disable_console_output(self):
        if not self.has_console_handler():
            return
        self.removeHandler(self.stdout_handler)

    def enable_console_output(self):
        if self.has_console_handler():
            return
        self.addHandler(self.stdout_handler)

    def disable_file_output(self):
        if not self.has_file_handler():
            return
        self.removeHandler(self.file_handler)

    def enable_file_output(self):
        if self.has_file_handler():
            return
        self.addHandler(self.file_handler)
