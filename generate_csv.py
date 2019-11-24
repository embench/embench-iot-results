#!/usr/bin/env python3

# Script to produce summary results as CSV

# Copyright (C) 2019 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Collate all Embench benchmark results

Data are held in files in the results directory of the form
<arch>-<description>.json.  Each defines a set of results in a JSON file.
"""

import argparse
import csv
import logging
import os
import re
import sys
import time

from json import loads
from json.decoder import JSONDecodeError

# All the global parameters
gparam = dict()


def build_parser():
    """Build a parser for all the arguments"""
    parser = argparse.ArgumentParser(description='Collate benchmark results')

    parser.add_argument(
        '--resdir',
        type=str,
        default='results',
        help='Directory holding the results files',
    )
    parser.add_argument(
        'resfiles',
        metavar='result-file',
        type=str,
        nargs='*',
        help='Specific results files to accumulate',
    )

    return parser


def validate_args(args):
    """Check that supplied args are all valid."""

    # Check the directory
    if os.path.isabs(args.resdir):
        gparam['resdir'] = args.resdir
    else:
        gparam['resdir'] = os.path.join(gparam['rootdir'], args.resdir)

    if not os.path.isdir(gparam['resdir']):
        print(f'ERROR: Results directory {gparam["resdir"]} not ' +
                   f'found: exiting')
        sys.exit(1)

    if not os.access(gparam['resdir'], os.R_OK):
        print(f'ERROR: Unable to read results directory ' +
                   f'{gparam["resdir"]}: exiting')
        sys.exit(1)

    # Enumerate the files
    gparam['resfiles'] = set()
    if args.resfiles:
        # Specific results files
        for resf in args.resfiles:
            abs_resf = os.path.join(gparam['resdir'], resf + '.json')
            if os.access(abs_resf, os.R_OK):
                gparam['resfiles'].add(resf)
            else:
                print(f'Warning: Unable to find result file '+
                             f'{resf}: ignored')
    else:
        # All results files
        dirlist = os.listdir(gparam['resdir'])
        for resf in dirlist:
            rootf, suffix = os.path.splitext(resf)
            abs_resf = os.path.join(gparam['resdir'], resf)
            if (suffix == '.json' and os.path.isfile(abs_resf) and
                    os.access(abs_resf, os.R_OK)):
                gparam['resfiles'].add(rootf)

    if not gparam['resfiles']:
        print(f'ERROR: No results files found')
        sys.exit(1)


def transcribe_results():
    """Transcribe the results from JSON to CSV"""

    with open('summary.csv', 'w', newline='') as csvfile:
        csvf = csv.writer(csvfile)

        # Header
        csvf.writerow([ 'Name',
                        'Size geomean',
                        'Size geosd',
                        'Speed geomean',
                        'Speed geosd', ])

        for resf in gparam['resfiles']:
            absf = os.path.join(gparam['resdir'], resf + '.json')
            with open(absf) as fileh:
                try:
                    resdata = loads(fileh.read())
                    row = [resdata['name'],]
                    if 'size results' in resdata:
                        row.append(
                            resdata['size results']['size geometric mean']
                        )
                        row.append(
                            resdata['size results']['size geometric standard deviation']
                        )
                    if 'speed results' in resdata:
                        row.append(
                            resdata['speed results']['speed geometric mean']
                        )
                        row.append(
                            resdata['speed results']['speed geometric standard deviation']
                        )
                    csvf.writerow (row)
                except JSONDecodeError as jex:
                    print(f'Warning: JSON results data error in {resf} '
                                f'at line {jex.lineno}, column {jex.colno}: '
                                f'{jex.msg}')
        # All done
        csvfile.close()


def main():
    """Main program to drive collating of benchmarks."""
    # Establish the root directory of the repository, since we know this file is
    # in that directory.
    gparam['rootdir'] = os.path.abspath(os.path.dirname(__file__))

    # Parse arguments using standard technology
    parser = build_parser()
    args = parser.parse_args()

    # Check args are OK (have to have logging directory set up first)
    validate_args(args)

    # Transcribe JSON into Markdown summary
    transcribe_results()


# Make sure we have new enough python
def check_python_version(major, minor):
    """Check the python version is at least {major}.{minor}."""
    if ((sys.version_info[0] < major)
            or ((sys.version_info[0] == major)
                and (sys.version_info[1] < minor))):
        print(f'ERROR: Requires Python {major}.{minor} or later')
        sys.exit(1)


# Make sure we have new enough Python and only run if this is the main package

check_python_version(3, 6)
if __name__ == '__main__':
    sys.exit(main())
