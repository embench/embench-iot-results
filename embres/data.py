#!/usr/bin/env python3

# Module to handle JSON Embench records as part of the embres package

# Copyright (C) 2019, 2020 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""Module with all the classes etc to capture Embench results from JSON files.

We have three main classes

- Record: The high level details of architecture, Embench version, descrption
  of the benchmark, Result for each category (size, speed, speed/MHz) and
  reference to DetailedRecord.

- Result: A record of geometric mean, geometric standard deviation, and
- derived from these low and high ranges (+/- one SD).

- DetailedRecord: All the data from the JSON file.

"""

from json import loads
from json.decoder import JSONDecodeError
import os
import sys


class Score:
    """
    A class to capture one set of scores (geometric mean and standard
    deviation) and compute the range derived from this.
    """
    def __init__(self, geomean, geosd):
        """
        Constructor sets the geometric mean and standard deviation.
        """
        # Sanity check
        assert (geomean >= 0.0), "Geometric mean must be >= 0.0."
        assert (geosd > 0.0), "Geometric standard deviation must be > 0.0."

        # Base values
        self.__geomean = geomean
        self.__geosd = geosd

    def geomean(self):
        """
        Accessor for the geometric mean
        """
        return self.__geomean

    def geosd(self):
        """
        Accessor for the geometric standard deviation
        """
        return self.__geosd

    def range_lo(self):
        """
        Accessor for the low end of the range
        """
        return self.__geomean / self.__geosd

    def range_hi(self):
        """
        Accessor for the high end of the range
        """
        return self.__geomean * self.__geosd


class ResultDetails:
    """
    All the data on a particular run held in its JSON file.
    """
    def __init__(self, resfile):
        """
        Initialize from a JSON file. If this fails, then the data will be
        empty and we set the error fields.

        Throws JSONDecodeError if the data is not valid
        """
        self.__resfile = resfile
        self.__json_data = None

        with open(resfile) as fileh:
            self.__json_data = loads(fileh.read())

    def desc(self):
        """
        Return the description. Only valid if we actually have data.
        """
        assert self.json_data, "No valid JSON data"
        return self.__json_data['description']

    def json_data(self):
        """
        Return the JSON data, which will be None if we have none
        """
        return self.__json_data

    def json_data_copy(self):
        """
        Return a copy of the JSON data, which can be safely manipulated
        without destroying the original. None if there is no data.
        """
        if self.__json_data:
            return self.__json_data.copy()

        return None

    def details_page(self):
        """
        Return the name of the wikipage which will hold the details.

        This is based on the JSON filename. We remove a .json suffix if it is
        there, otherwise we just use the basename.  Then add .mediawiki
        suffix.
        """
        basename = os.path.basename(self.__resfile)
        root, suffix = os.path.splitext(basename)

        # Sanity check
        if suffix == '.json':
            pagename = root + '.mediawiki'
        else:
            pagename = basename + '.mediawiki'

        return pagename

class InvalidResultError(Exception):
    """
    User exception when we have invalid JSON data for a result

    Attributes:
        missing_fields -- top level fields missing from the JSON data
        missing_platform_fields - fields missing from platform info
    """
    def __init__(self, missing_fields, missing_platform_fields):
        """
        Initialize with two lists, one of top level JSON fields missing, one
        with platform info fields missing.
        """
        super(InvalidResultError, self).__init__()
        self.missing_fields = missing_fields
        self.missing_platform_fields = missing_platform_fields


class Result:
    """
    Top level record of a result. Its contents are mostly derived from the
    ResultDetails, but potentially supplemented by a link to a page with
    details of the actual run.
    """
    def __validate_data(self):
        """
        Determine if the supplied data is valid, logging any omissions if a
        log file is provided.

        Raises InvalidResultError if the JSON data is not good.
        """
        json_data = self.__result_details.json_data()

        # We shouldn't be able to get here without data
        assert json_data, "No JSON data for Result"

        # Must have key fields
        missing_fields = set()
        fields = {
            'description', 'architecture family', 'Embench version',
        }

        for field in fields:
            if not field in json_data:
                missing_fields.add(field)

        # Must have certain platform info
        field = 'platform information'
        missing_pfields = set()
        if field in json_data:
            pfields = {
                'nominal clock rate (MHz)',
                'max clock rate (MHz)',
                'isa',
                'address size (bits)',
                'processor version',
                'number of enabled cores',
                'hardware threads per core',
                'caches',
                'thermal design power',
                'program memory size (kB)',
                'data memory size (kB)',
                'storage',
                'external memory',
                'external buses',
                'misc accellerators and I/O devices',
                'OS and version',
            }
            pinfo = json_data[field]

            for pfield in pfields:
                if not pfield in pinfo:
                    missing_pfields.add(pfield)
        else:
            missing_fields.add(field)

        if missing_fields or missing_pfields:
            raise InvalidResultError(missing_fields, missing_pfields)

    def __init__(self, resfile):
        """
        Initialize from a JSON file.

        May pass on the following exceptions:

            JSONDecodeError -- the JSON file was not well formatted
            InvalidResultError -- Fields were missing or invalid in the JSON
        """
        # Get the raw data and check it is good.
        self.__result_details = ResultDetails(resfile)
        self.__validate_data()

        # Now have good data.
        json_data = self.__result_details.json_data()

        # Collect data
        self.__scores = dict()

        # Size data
        if 'relative size results' in json_data:
            size_data = json_data['relative size results']
            self.__scores['Size'] = Score(
                size_data['geometric mean'],
                size_data['geometric standard deviation']
            )
        else:
            self.__scores['Size'] = None

        # Speed data in file is per MHz
        if 'relative speed results' in json_data:
            speed_data = json_data['relative speed results']
            self.__scores['Speed/MHz'] = Score(
                speed_data['geometric mean'],
                speed_data['geometric standard deviation']
            )
            self.__scores['Speed'] = Score(
                self.__scores['Speed/MHz'].geomean() * self.cpu_mhz(),
                self.__scores['Speed/MHz'].geosd()
            )
        else:
            self.__scores['Speed'] = None
            self.__scores['Speed/MHz'] = None

    def desc(self):
        """
        Accessor for the test desc.
        """
        return self.__result_details.json_data()['description']

    def arch(self):
        """
        Accessor for the architecture family.
        """
        return self.__result_details.json_data()['architecture family']

    def embench_version(self):
        """
        Accessor for the Embench version
        """
        return self.__result_details.json_data()['Embench version']

    def cpu_mhz(self):
        """
        Accessor for the clock speed used for the test
        """
        pinfo = self.__result_details.json_data()['platform information']
        return pinfo['nominal clock rate (MHz)']

    def scores(self):
        """
        Accessor for the list of scores associated with this test.
        """
        return self.__scores

    def details(self):
        """
        Accessor for the detailed results.
        """
        return self.__result_details

    def details_page(self):
        """
        Accessor for the details wikipage.
        """
        return self.__result_details.details_page()


class ResultSet:
    """
    Collection of results. This is primarily to encapsulate the process of
    enumerating and reading all the result files.
    """
    @staticmethod
    def __collate_files(rootdir, log, resdir, resfiles):
        """
        Collate all the result files. It must be a list so we can sort it.
        """
        # Build up a list.
        filelist = []
        if resfiles:
            # Specific results files from the command line
            for resf in resfiles:
                if os.path.isabs(resf):
                    filelist.append(resf)
                else:
                    absresf = os.path.join(resdir, resf)
                    if os.access(absresf, os.R_OK):
                        filelist.append(absresf)
                    else:
                        absresf = os.path.join(rootdir, resf)
                        if os.access(absresf, os.R_OK):
                            filelist.append(absresf)
                        else:
                            log.warning(f'Warning: Unable to find result file '
                                        f'{resf}: ignored')
        else:
            # All results files. No need to sort them, since they'll get
            # sorted later.
            dirlist = os.listdir(resdir)
            for resf in dirlist:
                _, suffix = os.path.splitext(resf)
                absresf = os.path.join(resdir, resf)
                if (suffix == '.json' and os.path.isfile(absresf) and
                        os.access(absresf, os.R_OK)):
                    filelist.append(absresf)

        # Sanity check
        if not filelist:
            log.error(f'ERROR: No results files found')
            sys.exit(1)

        return filelist

    def __init__(self, rootdir, log, resdir, resfiles):
        """
        If we are given a list of resfiles, then read each as a JSON file to
        get the result details, otherwise enumerate all files with the suffix
        '.json' in the resdir.

        Relative files are looked for first relative to resdir, then relative
        to rootdir
        """
        # Build up a list of files that may contain results
        filelist = self.__collate_files(rootdir, log, resdir, resfiles)

        # Now open each in turn and build up a list of results
        self.__results = []
        for resf in filelist:
            # Reading JSON data may fail and is caught here.
            result = None
            try:
                result = Result(resf)
            except JSONDecodeError as jex:
                log.warning(
                    f'Warning: {resf}: Invalid JSON data at line ' +
                    f'{jex.lineno}, column {jex.colno}: {jex.msg}: ' +
                    f'result file ignored.'
                )
            except InvalidResultError as irex:
                for mfield in irex.missing_fields:
                    log.debug(f'{resf}: Missing JSON field {mfield}')
                for mpfield in irex.missing_platform_fields:
                    log.debug(
                        f'{resf}: Missing JSON plaform info field {mpfield}'
                    )
                log.warning(
                    f'Warning: {resf}: Missing JSON fields: result file ignored.'
                )

            if result:
                self.__results.append(result)

    def sort(self, key, reverse):
        """
        Sort the list of results. Arguments are the same as to the sorted
        function.
        """
        self.__results = sorted(self.__results, key=key, reverse=reverse)

    def results(self):
        """
        Accessor for the list of results.
        """
        return self.__results
