#!/usr/bin/env python3

# Module to handle arguments as part of the embres package

# Copyright (C) 2019, 2020 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Module to handle argument parsing.

We break this into two stages.

- an initial parse to get the raw arguments, so the log file can be set up

- a post processing phase to validate and sanitize the arguments.
"""


import argparse
import os
import re
import sys


class Args:
    """
    A class to handle argument parsing
    """
    def __init__(self, rootdir):
        """
        Parse the raw arguments. The goal is to get enough information we can
        set up logging. We need to know the root directory, since ultimately
        relative file arguments will be based on this.
        """
        # Capture the root directory
        self.__rootdir = rootdir

        # Create a parser
        parser = argparse.ArgumentParser(description='Collate benchmark results')

        # Add the arguments
        parser.add_argument(
            '--resdir',
            type=str,
            default=None,
            help='Directory holding the results files',
        )
        parser.add_argument(
            '--detailsdir',
            type=str,
            default='details',
            help='Directory holding the detail of results wikified'
        )
        parser.add_argument(
            '--logdir',
            type=str,
            default='logs',
            help='Directory in which to store logs',
        )
        parser.add_argument(
            'resfiles',
            metavar='result-file',
            type=str,
            nargs='*',
            help='Specific results files to accumulate',
        )

        # Parse the command line
        self.__raw = parser.parse_args()

        # Mark all private copies as empty for now.
        self.__cooked = dict()
        self.__cooked['abslogdir'] = None
        self.__cooked['absresdir'] = None
        self.__cooked['detailsdir'] = None
        self.__cooked['readme_hdr'] = None
        self.__cooked['readme'] = None
        self.__cooked['resfiles'] = []

    def abslogdir(self):
        """
        Extract the log directory, create it if necessary and make sure it is
        writable. This means dealing with relative v absolute directory
        names. Any errors here are going to go straight to the console as
        exceptions.
        """
        # Cache the result
        if not self.__cooked['abslogdir']:
            # Sort out absolutism
            logdir = self.__raw.logdir
            if os.path.isabs(logdir):
                abslogdir = logdir
            else:
                abslogdir = os.path.join(self.__rootdir, logdir)

            # Create the directory if necessary and make sure we can write it.
            if not os.path.isdir(abslogdir):
                try:
                    os.makedirs(abslogdir)
                except PermissionError:
                    raise PermissionError(
                        f'Unable to create log directory {logdir}'
                    )

            if not os.access(abslogdir, os.W_OK):
                raise PermissionError(
                    f'Unable to write to log directory {logdir}'
                )

            self.__cooked['abslogdir'] = abslogdir

        return self.__cooked['abslogdir']

    def __absresdir(self, log):
        """
        Private method to sort out the results directory, which should end up
        as an (existing) absolute directory that is readable.
        """
        # Cache the result
        if not self.__cooked['absresdir']:
            resdir = self.__raw.resdir
            if resdir:
                if os.path.isabs(resdir):
                    absresdir = resdir
                else:
                    absresdir = os.path.join(self.__rootdir, resdir)
            else:
                absresdir = self.__rootdir

            # Directory exists and is readable?
            if not os.path.isdir(absresdir):
                log.error(f'ERROR: Results directory {resdir} not ' +
                          f'found: exiting')
                sys.exit(1)

            if not os.access(absresdir, os.R_OK):
                log.error(f'ERROR: Unable to read results directory ' +
                          f'{resdir}: exiting')
                sys.exit(1)

            self.__cooked['absresdir'] = absresdir

    def __detailsdir(self, log):
        """
        Private method to sort out the details directory, which we create if it
        does not exist.  This *must* be relative to the root directory.  We
        should end up with a directory that is writable.
        """
        # Cache the result
        if not self.__cooked['detailsdir']:
            detailsdir = self.__raw.detailsdir
            if os.path.isabs(detailsdir):
                log.error(
                    f'ERROR: Details directory {detailsdir} cannot be '
                    f'absolute: exiting'
                )
                sys.exit(1)

            # Absolute directory
            absdetailsdir = os.path.join(self.__rootdir, detailsdir)

            # Create the directory if needed and check it is writable.
            if not os.path.isdir(absdetailsdir):
                try:
                    os.makedirs(absdetailsdir)
                except PermissionError:
                    log.error(
                        f'ERROR: Unable to create details directory ' +
                        f'{detailsdir}: exiting')
                    sys.exit(1)

            if not os.access(absdetailsdir, os.W_OK):
                log.error(f'ERROR: Unable to write details directory ' +
                          f'{detailsdir}: exiting')
                sys.exit(1)

            # Need the name both absolute and relative.
            self.__cooked['absdetailsdir'] = absdetailsdir
            self.__cooked['detailsdir'] = detailsdir

    def __readme(self, log):
        """
        Private method to sort out the README files. The README header must
        exist and be readable. The new README must be available for writing.
        The README header is opened for reading and the new README  opened for
        writing.
        """
        # Cache the result
        if not (self.__cooked['readme_hdr'] and self.__cooked['readme']):
            readme_hdr = os.path.join(self.__rootdir, 'README-header.mediawiki')
            readme = os.path.join(self.__rootdir, 'README.mediawiki')

            # Try to open the README header for reading, if it is not already
            # opened.
            if not self.__cooked['readme_hdr']:
                # Old readme should exist.
                try:
                    self.__cooked['readme_hdr'] = open(readme_hdr, 'r')
                except OSError as osex:
                    log.error(f'ERROR: Could not open {readme_hdr} for ' +
                              f'reading: {osex.strerror}')
                    sys.exit(1)

            # Try to open the new README for writing, if it is not already
            # opened.
            if not self.__cooked['readme']:
                try:
                    self.__cooked['readme'] = open(readme, 'w')
                except OSError as osex:
                    log.error(f'ERROR: Could not open {readme} for writing: ' +
                              f'{osex.strerror}')
                    sys.exit(1)

    def __resfiles(self):
        """
        Collate the results files as a list of absolute file names on the
        command line.
        """
        # Cache the result
        if not self.__cooked['resfiles']:
            # Enumerate the files
            self.__cooked['resfiles'] = self.__raw.resfiles

    def all_args(self, log):
        """
        Sort out all the arguments, other than the logdir. Any diagnostics
        take advantage of the supplied log.

        The result is a dictionary of processed arguments. Note that this can
        be called multiple times - after the first time, it will just return
        the result from the first call.
        """
        # Results and details directories
        self.__absresdir(log)
        self.__detailsdir(log)

        # New and old readme files as needed. Note that these are file handles.
        self.__readme(log)

        # Collate all the files to be processed.
        self.__resfiles()

        return self.__cooked

    def __log_raw(self, log):
        """
        Record the raw argument values
        """
        log.debug('Supplied raw arguments')
        log.debug('======================')

        for arg in vars(self.__raw):
            realarg = re.sub('_', '-', arg)
            val = getattr(self.__raw, arg)
            log.debug(f'--{realarg:20}: {val}')

        log.debug('')

    def __log_cooked(self, log):
        """
        Record the cooked argument values. No point in printing file handles!
        """
        log.debug('Supplied cooked arguments')
        log.debug('=========================')

        log.debug('Results directory: ' + self.__cooked['absresdir'])

        log.debug('Results files to process:')
        for resf in self.__cooked['resfiles']:
            log.debug('  ' + resf)

        log.debug('')

    def log_args(self, log):
        """
        Convenience method to log both raw and cooked args
        """
        self.__log_raw(log)
        self.__log_cooked(log)
