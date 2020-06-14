#!/usr/bin/env python3

# Module to handle logging as part of the embres package

# Copyright (C) 2019, 2020 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""Module with all the classes etc to handle logging.

We have three main classes

- Record: The high level details of architecture, Embench version, Name of the
  benchmark, Result for each category (size, speed, speed/MHz) and reference
  to DetailedRecord.

- Result: A record of geometric mean, geometric standard deviation, and
- derived from these low and high ranges (+/- one SD).

- DetailedRecord: All the data from the JSON file.
"""

import logging
import os
import time
import sys


class Logger:
    """
    A class to capture all logging activity.
    """
    def __init__(self, abs_logdir, prefix):
        """
        Initialize logging. The log file has a timestamped name based on
        prefix and lives in the supplied absolute log directory.

        Debug messages only go to file, everything else also goes to the
        console.
        """
        # First create the log directory if needed
        if not os.path.isdir(abs_logdir):
            try:
                os.makedirs(abs_logdir)
            except PermissionError:
                raise PermissionError(
                    f'Unable to create log directory {abs_logdir}'
                )

        if not os.access(abs_logdir, os.W_OK):
            raise PermissionError(
                f'Unable to write to log directory {abs_logdir}'
            )

        # Now set up logging in the specified directory.
        logfile = os.path.join(
            abs_logdir, time.strftime(f'{prefix}-%Y-%m-%d-%H%M%S.log')
        )

        # Handle for the logger
        self.__log = logging.getLogger()

        # Configure logging to the console
        self.__log.setLevel(logging.DEBUG)
        console_h = logging.StreamHandler(sys.stdout)
        console_h.setLevel(logging.INFO)
        self.__log.addHandler(console_h)

        # Configure logging to the log file
        file_h = logging.FileHandler(logfile)
        file_h.setLevel(logging.DEBUG)
        self.__log.addHandler(file_h)

        # Log where the log file is
        self.__log.debug('Log file: %s\n', logfile)
        self.__log.debug('')

    def info(self, msg):
        """
        Log a message to the console and log file
        """
        self.__log.info(msg)

    def debug(self, msg):
        """
        Log a message to the console and log file
        """
        self.__log.debug(msg)

    def warning(self, msg):
        """
        Log a warning message to the console and log file.
        """
        self.__log.warning(msg)

    def error(self, msg):
        """
        Log an error message to the console and log file.
        """
        self.__log.error(msg)
