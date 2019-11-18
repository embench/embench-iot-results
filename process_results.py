#!/usr/bin/env python3

# Script to collate all benchmark results

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
import logging
import os
import re
import sys
import time

from json import loads
from json.decoder import JSONDecodeError

# Handle for the logger
logh = logging.getLogger()

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
        '--logdir',
        type=str,
        default='logs',
        help='Directory in which to store logs',
    )
    parser.add_argument(
        '--new-readme',
        type=str,
        default='README-new.md',
        help='Where to write the new README.md',
    )
    parser.add_argument(
        'resfiles',
        metavar='result-file',
        type=str,
        nargs='*',
        help='Specific results files to accumulate',
    )

    return parser


def create_logdir(logdir):
    """Create the log directory, which can be relative to the root directory
       or absolute"""
    if not os.path.isabs(logdir):
        logdir = os.path.join(gparam['rootdir'], logdir)

    if not os.path.isdir(logdir):
        try:
            os.makedirs(logdir)
        except PermissionError:
            raise PermissionError(f'Unable to create log directory {logdir}')

    if not os.access(logdir, os.W_OK):
        raise PermissionError(f'Unable to write to log directory {logdir}')

    return logdir


def setup_logging(logdir, prefix):
    """Set up logging in the directory specified by "logdir".

       The log file name is the "prefix" argument followed by a timestamp.

       Debug messages only go to file, everything else also goes to the
       console."""

    # Create the log directory first if necessary.
    logdir_abs = create_logdir(logdir)
    logfile = os.path.join(
        logdir_abs, time.strftime(f'{prefix}-%Y-%m-%d-%H%M%S.log')
    )

    # Set up logging
    logh.setLevel(logging.DEBUG)
    cons_h = logging.StreamHandler(sys.stdout)
    cons_h.setLevel(logging.INFO)
    logh.addHandler(cons_h)
    file_h = logging.FileHandler(logfile)
    file_h.setLevel(logging.DEBUG)
    logh.addHandler(file_h)

    # Log where the log file is
    logh.debug(f'Log file: {logfile}\n')
    logh.debug('')


def log_args(args):
    """Record all the argument values"""
    logh.debug('Supplied arguments')
    logh.debug('==================')

    for arg in vars(args):
        realarg = re.sub('_', '-', arg)
        val = getattr(args, arg)
        logh.debug(f'--{realarg:20}: {val}')

    logh.debug('')


def validate_resdir(args):
    """Check the details of the results directory are OK and enumerate the
       files."""

    # Check the directory
    if os.path.isabs(args.resdir):
        gparam['resdir'] = args.resdir
    else:
        gparam['resdir'] = os.path.join(gparam['rootdir'], args.resdir)

    if not os.path.isdir(gparam['resdir']):
        logh.error(f'ERROR: Results directory {gparam["resdir"]} not ' +
                   f'found: exiting')
        sys.exit(1)

    if not os.access(gparam['resdir'], os.R_OK):
        logh.error(f'ERROR: Unable to read results directory ' +
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
                logh.warning(f'Warning: Unable to find result file '+
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
        logh.error(f'ERROR: No results files found')
        sys.exit(1)

def validate_readme(args):
    """Check the README files are OK."""

    readme_old = os.path.join(gparam['rootdir'], 'README.md')

    if os.path.isabs(args.new_readme):
        readme_new = args.new_readme
    else:
        readme_new = os.path.join(gparam['rootdir'], args.new_readme)

    if os.path.exists(readme_new) and os.path.samefile(readme_new, readme_old):
        logh.error(f'ERROR: New README file {readme_new} must differ from '
                   f'existing file, {readme_old}')
        sys.exit(1)

    try:
        gparam['readme_oldf'] = open(readme_old, "r")
    except OSError as osex:
        logh.error(f'ERROR: Could not open {readme_old} for reading: ' +
                   f'{osex.strerror}')
        sys.exit(1)

    try:
        gparam['readme_newf'] = open(readme_new, "w")
    except OSError as osex:
        logh.error(f'ERROR: Could not open {readme_new} for writing: ' +
                   f'{osex.strerror}')
        sys.exit(1)


def validate_args(args):
    """Check that supplied args are all valid. By definition logging is
       working when we get here.

       Update the gparam dictionary with all the useful info"""

    # Validate the results directory
    validate_resdir(args)

    # Sort out the README file
    validate_readme(args)


def output_markdown_line(resdata):
    """Output a line of a markdown table of results"""

    name = resdata['name']
    clk_rate = resdata['nominal clock rate (MHz)']

    # Compute the entries
    size = {
        'geomean' : resdata['size geometric mean'],
        'geosd' : resdata['size geometric standard deviation'],
    }

    size['lo'] = size['geomean'] / size['geosd']
    size['hi'] = size['geomean'] * size['geosd']

    size_rel = {
        'geomean' : size['geomean'] / clk_rate,
        'geosd' : size['geosd'],
    }

    size_rel['lo'] = size_rel['geomean'] / size_rel['geosd']
    size_rel['hi'] = size_rel['geomean'] * size_rel['geosd']

    speed = {
        'geomean' : resdata['speed geometric mean'],
        'geosd' : resdata['speed geometric standard deviation'],
    }

    speed['lo'] = speed['geomean'] / speed['geosd']
    speed['hi'] = speed['geomean'] * speed['geosd']

    speed_rel = {
        'geomean' : speed['geomean'] / clk_rate,
        'geosd' : speed['geosd'],
    }

    speed_rel['lo'] = speed_rel['geomean'] / speed_rel['geosd']
    speed_rel['hi'] = speed_rel['geomean'] * speed_rel['geosd']

    # Generate the rows
    gparam['readme_newf'].writelines('|                             ' +
                                     '|      ' +
                                     '|           ' +
                                     '|         |         |         |\n')
    gparam['readme_newf'].writelines(f'| {name:27} ' +
                                     f'| {clk_rate:4} ' +
                                     f'| Size      ' +
                                     f'| {size["geomean"]:7.2f} ' +
                                     f'| {size["lo"]:7.2f} ' +
                                     f'| {size["hi"]:7.2f} |\n')
    gparam['readme_newf'].writelines(f'|                             ' +
                                     f'|      ' +
                                     f'| Size/MHz  ' +
                                     f'| {size_rel["geomean"]:7.2f} ' +
                                     f'| {size_rel["lo"]:7.2f} ' +
                                     f'| {size_rel["hi"]:7.2f} |\n')
    gparam['readme_newf'].writelines(f'|                             ' +
                                     f'|      ' +
                                     f'| Speed     ' +
                                     f'| {speed["geomean"]:7.2f} ' +
                                     f'| {speed["lo"]:7.2f} ' +
                                     f'| {speed["hi"]:7.2f} |\n')
    gparam['readme_newf'].writelines(f'|                             ' +
                                     f'|      ' +
                                     f'| Speed/MHz ' +
                                     f'| {speed_rel["geomean"]:7.2f} ' +
                                     f'| {speed_rel["lo"]:7.2f} ' +
                                     f'| {speed_rel["hi"]:7.2f} |\n')


def transcribe_results():
    """Transcribe the results from JSON to Markdown"""

    # Header from README.md
    for line in gparam['readme_oldf']:
        gparam['readme_newf'].writelines(line)
        if '<!-- Insert results here -->' in line:
            break

    # Table of data
    gparam['readme_newf'].writelines('\n')
    gparam['readme_newf'].writelines('| Benchmark name              ' +
                                     '|  MHz ' +
                                     '| Type      ' +
                                     '|   Score |     Low |    High |\n')
    gparam['readme_newf'].writelines('| --------------------------- ' +
                                     '| ----:' +
                                     '|:---------:' +
                                     '| -------:| -------:| -------:|\n')

    for resf in gparam['resfiles']:
        absf = os.path.join(gparam['resdir'], resf + '.json')
        with open(absf) as fileh:
            try:
                resdata = loads(fileh.read())
                logh.info(resdata['name'])
                output_markdown_line(resdata)
            except JSONDecodeError as jex:
                logh.warning(f'Warning: JSON results data error in {resf} '
                             f'at line {jex.lineno}, column {jex.colno}: '
                             f'{jex.msg}')

    # Footer from README.md
    gparam['readme_newf'].writelines('\n')

    for line in gparam['readme_oldf']:
        if '<!-- Results end here -->' in line:
            gparam['readme_newf'].writelines(line)
            break

    for line in gparam['readme_oldf']:
        gparam['readme_newf'].writelines(line)


def main():
    """Main program to drive collating of benchmarks."""
    # Establish the root directory of the repository, since we know this file is
    # in that directory.
    gparam['rootdir'] = os.path.abspath(os.path.dirname(__file__))

    # Parse arguments using standard technology
    parser = build_parser()
    args = parser.parse_args()

    # Establish logging, using "build" as the log file prefix.
    setup_logging(args.logdir, 'build')
    log_args(args)

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
        logh.error(f'ERROR: Requires Python {major}.{minor} or later')
        sys.exit(1)


# Make sure we have new enough Python and only run if this is the main package

check_python_version(3, 6)
if __name__ == '__main__':
    sys.exit(main())
