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

# System packages
import os.path
import sys

# Local packages
import embres


def main():
    """
    Main program to drive collating of benchmarks.
    """
    # Parse the arguments, set up logging and then validate the arguments
    rootdir = os.path.abspath(os.path.dirname(__file__))
    args = embres.Args(rootdir)
    log = embres.Logger(args.abslogdir(), 'results')
    arglist = args.all_args(log)
    args.log_args(log)

    # Read all the data
    reslist = embres.ResultSet(
        rootdir, log, arglist['absresdir'], arglist['resfiles']
    )

    # Create the new readme
    readme = embres.Readme(
        arglist['readme_hdr'],
        arglist['readme'],
        arglist['absdetailsdir'],
        arglist['detailsdir']
    )

    # Create all the details files
    if reslist:
        readme.write_all_details(reslist)
    else:
        log.error('ERROR: No results found')
        sys.exit(1)

    # Header for the main README
    readme.write_header()

    # Results sorted by speed (large is good)
    reslist.sort(
        key=lambda rec: rec.scores()['Speed'].geomean(), reverse=True
    )
    readme.write_table('Results sorted by Embench speed score', reslist)

    # Results sorted by speed/MHz (large is good)
    reslist.sort(
        key=lambda rec: rec.scores()['Speed/MHz'].geomean(), reverse=True
    )
    readme.write_table('Results sorted by Embench speed score/MHz', reslist)

    # Results sorted by size (small is good)
    reslist.sort(key=lambda rec: rec.scores()['Size'].geomean(), reverse=False)
    readme.write_table('Results sorted by Embench size score', reslist)

    # Per architecture results sorted by speed (large is good)
    reslist.sort(key=lambda rec: rec.scores()['Speed'].geomean(), reverse=True)
    reslist.sort(key=lambda rec: rec.arch(), reverse=False)
    readme.write_table(
        'Per architecture results sorted by Embench speed score', reslist
    )

    # Per architecture results sorted by speed/MHz (large is good)
    reslist.sort(
        key=lambda rec: rec.scores()['Speed/MHz'].geomean(), reverse=True
    )
    reslist.sort(key=lambda rec: rec.arch(), reverse=False)
    readme.write_table(
        'Per architecture results sorted by Embench speed score/MHz', reslist
    )

    # Per architecture results sorted by size (small is good)
    reslist.sort(key=lambda rec: rec.scores()['Size'].geomean(), reverse=False)
    reslist.sort(key=lambda rec: rec.arch(), reverse=False)
    readme.write_table(
        'Per achitecture results sorted by Embench size score', reslist
    )


# Make sure we have new enough Python and only run if this is the main package
embres.check_python_version(3, 6)
if __name__ == '__main__':
    sys.exit(main())
