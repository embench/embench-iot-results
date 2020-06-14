#!/usr/bin/env python3

# Module to generate the new README as part of the embres package

# Copyright (C) 2019, 2020 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Module to generate a new README and the subsidiary pages

This can be summarized as generating the header, then generating a series of
sections based on different orderings.
"""

# System packages
import os.path


class Readme:
    """
    A class to handle README file generation
    """
    def __init__(self, readme_hdr, readme, absdetailsdir, detailsdir):
        """
        The constructor just keeps a copy of the file handles, creates a
        writer for details pages and the relative directory with pages of
        details.
        """
        # Sanity check
        assert os.path.isabs(absdetailsdir), f'{absdetailsdir} is relative'

        # Record the file handle.
        self.__readme_hdr = readme_hdr
        self.__readme = readme
        self.__absdetailsdir = absdetailsdir
        self.__detailsdir = detailsdir

    def __wiki_tblhdr(self):
        """
        Private method to write out the standard wiki table header.
        """
        # Header is all fixed.
        self.__readme.writelines('{| class="wikitable sortable"\n')
        self.__readme.writelines('! align="left"  | Architecture\n')
        self.__readme.writelines('! align="left"  | Benchmark description\n')
        self.__readme.writelines('! align="right" | MHz\n')
        self.__readme.writelines('! align="left"  | Type\n')
        self.__readme.writelines('! align="right" | Score\n')
        self.__readme.writelines('! align="center" | Range\n')

    def __wiki_tblrow(self, res):
        """
        Private method to write out one row of wiki table data for the
        supplied result file.
        """
        # Put out the lines
        self.__readme.writelines(f'|- align="left"\n')
        self.__readme.writelines(f'|  rowspan="3" | {res.arch()}\n')
        dref = f'{self.__detailsdir}/{res.details_page()}'
        self.__readme.writelines(f'|  rowspan="3" | [[{dref}|{res.desc()}]]\n')
        self.__readme.writelines(f'|  align="right" rowspan="3" | '
                                 f'{res.cpu_mhz()}\n')

        # Line for each type of result
        resvals = res.scores()

        for rtype in ['Size', 'Speed', 'Speed/MHz']:
            rval = resvals[rtype]

            self.__readme.writelines(f'|  {rtype}\n')
            self.__readme.writelines(f'|  align="right" | '
                                     f'{rval.geomean():.2f}\n')
            self.__readme.writelines(f'|  align="center" | '
                                     f'{rval.range_lo():.2f}'
                                     f'- {rval.range_hi():.2f}\n')
            self.__readme.writelines(f'|-\n')

    def __wiki_tblftr(self):
        """
        Private method to write out the standard wiki footer.
        """
        # Footer
        self.__readme.writelines('|}\n')

    def write_header(self):
        """
        Copy the fixed pre-header into the README.
        """
        for line in self.__readme_hdr:
            self.__readme.writelines(line)

    @staticmethod
    def __write_general_details(fileh, json_data):
        """
        Static method to write out general detail fields.

        Will raise KeyError if the description field is missing
        """
        # Page title is the description
        desc = json_data.pop('description')
        fileh.writelines(f'== {desc} ==\n\n')

        # Table for the info
        fileh.writelines('{| class="wikitable sortable"\n')

        fields = ['Embench version', 'architecture family', 'date/time',]
        for field in fields:
            val = json_data.pop(field, '')
            fileh.writelines(f'|- align="left"\n')
            fileh.writelines(f'| {field} || {val}\n')

        fileh.writelines('|}\n\n')

    @staticmethod
    def __write_platform_info(fileh, json_data):
        """
        Static method to write out platform information fields.

        Will raise KeyError if the platform information field is missing
        """
        # Section title is the description
        pinfo = json_data.pop('platform information')
        fileh.writelines('== Platform information ==\n\n')

        # Table for the info
        fileh.writelines('{| class="wikitable sortable"\n')

        for field, val in pinfo.items():
            fileh.writelines(f'|- align="left"\n')
            fileh.writelines(f'| {field} || {val}\n')

        fileh.writelines('|}\n\n')

    @staticmethod
    def __write_tool_chain_info(fileh, json_data):
        """
        Static method to write out tool chain info fields.

        Will raise KeyError if the tool chain information, tool chain version
        or tool chain flag fields are missing
        """
        # Main section title
        tcinfo = json_data.pop('tool chain information')
        fileh.writelines('== Tool chain information ==\n\n')

        # Section for tool chain version
        tcvinfo = tcinfo.pop('tool chain version')
        fileh.writelines('=== Tool chain versions ===\n\n')

        # Table for the tool chain version info
        fileh.writelines('{| class="wikitable sortable"\n')

        for field, val in tcvinfo.items():
            fileh.writelines(f'|- align="left"\n')
            fileh.writelines(f'| {field} || {val}\n')

        fileh.writelines('|}\n\n')

        # Section for tool chain flags
        tcfinfo = tcinfo.pop('tool chain flags')
        fileh.writelines('=== Tool chain flags used in benchmarking ===\n\n')

        # Table for the tool chain flags info
        fileh.writelines('{| class="wikitable sortable"\n')

        for field, val in tcfinfo.items():
            # Flag values are a list of flags
            flagstr = ""
            for flag in val:
                if flagstr:
                    flagstr = f'{flagstr} {flag}'
                else:
                    flagstr = f'{flag}'
            fileh.writelines(f'|- align="left"\n')
            fileh.writelines(f'| {field} || {flagstr}\n')

        fileh.writelines('|}\n\n')

        # Section for any other tool chain info
        if tcinfo:
            fileh.writelines('=== Other tool chain information ===\n\n')

            # Table for the other tool chain info
            fileh.writelines('{| class="wikitable sortable"\n')

            for field, val in tcinfo.items():
                fileh.writelines(f'|- align="left"\n')
                fileh.writelines(f'| {field} || {val}\n')

            fileh.writelines('|}\n\n')

    @staticmethod
    def __write_detailed_results(fileh, json_data):
        """
        Static method to write out detailed results.
        """
        # Section title
        fileh.writelines('== Detailed Embench results ==\n\n')

        # What section types are included in size data
        sectypes = json_data.pop('sections in size results', None)

        # Section values are a list of section types
        if sectypes:
            secstr = ""
            for sec in sectypes:
                if secstr:
                    secstr = f'{secstr} {sec}'
                else:
                    secstr = f'{sec}'
            fileh.writelines(f'Section types included in size data: {secstr}\n')

        # Collate data, so we can tabulate. This is a dictionary keyed by the
        # benchmark name. The values are themselves 4 element dictionaries,
        # keyed as 'abs_size', 'rel_size', 'abs_speed' and 'rel_speed'

        all_res = {
            'abs_size' : json_data.pop('absolute size results', None),
            'rel_size' : json_data.pop('relative size results', None),
            'abs_speed' : json_data.pop('absolute speed results', None),
            'rel_speed' : json_data.pop('relative speed results', None),
        }

        results = dict()
        for restype in {'abs_size', 'rel_size', 'abs_speed', 'rel_speed'}:
            data = all_res[restype].pop('detailed results')
            for benchmark, val in data.items():
                if not benchmark in results:
                    results[benchmark] = dict()
                results[benchmark][restype] = val

        # Put the results in a table
        fileh.writelines('{| class="wikitable sortable"\n')
        fileh.writelines('! align="left"  |\n')
        fileh.writelines('! colspan="2" align="center" | Size\n')
        fileh.writelines('! colspan="2" align="center" | Speed/MHz\n')
        fileh.writelines('|- align="left"\n')
        fileh.writelines('! align="left" | Benchmark\n')
        fileh.writelines('! align="right"  | Absolute\n')
        fileh.writelines('! align="right" | Relative\n')
        fileh.writelines('! align="right"  | Absolute\n')
        fileh.writelines('! align="right" | Relative\n')

        for benchmark, res in results.items():
            fileh.writelines(f'|- align="left"\n')
            fileh.writelines(f'| {benchmark}\n')
            for restype in ['abs_size', 'rel_size', 'abs_speed', 'rel_speed']:
                # Absolute values are large, relative small.
                if restype in ['abs_size', 'abs_speed']:
                    fileh.writelines(f'| align="right" | {res[restype]:,}\n')
                else:
                    fileh.writelines(f'| align="right" | {res[restype]:,.2f}\n')

        # Geometric mean and SD
        fileh.writelines(f'|- align="left"\n')
        fileh.writelines(f'! Geometric mean\n')
        for restype in ['rel_size', 'rel_speed']:
            geomean = all_res[restype].pop('geometric mean')
            fileh.writelines(f'!\n')
            fileh.writelines(f'! align="right" | {geomean:,.2f}\n')

        fileh.writelines(f'|- align="left"\n')
        fileh.writelines(f'! Geometric standard deviation\n')
        for restype in ['rel_size', 'rel_speed']:
            geosd = all_res[restype].pop('geometric standard deviation')
            fileh.writelines(f'!\n')
            fileh.writelines(f'! align="right" | {geosd:,.2f}\n')

        fileh.writelines('|}\n\n')

    @staticmethod
    def __write_other(fileh, json_data, hdr_intro, title):
        """
        Static method to write out any remaining data.

        If we have a dictionary as value, we write they key out as a heading
        and recurse to write the rest.
        """
        # May have nothing!
        if not json_data:
            return

        # Have something, give it a title
        fileh.writelines(f'{hdr_intro} {title} {hdr_intro}\n\n')

        # Deal with scalar values first.
        scalar_vals = dict()
        for key, val in json_data.items():
            if not isinstance(val, dict):
                scalar_vals[key] = val

        # Write out a table of scalar values
        if scalar_vals:
            fileh.writelines('{| class="wikitable sortable"\n')
            for key, val in scalar_vals.items():
                fileh.writelines(f'|- align="left"\n')
                fileh.writelines(f'| {key} || {val}\n')
            fileh.writelines('|}\n\n')


        # Now write any dictionaries in their own subsections.
        for key, val in json_data.items():
            if isinstance(val, dict):
                Readme.__write_other(
                    fileh, val, hdr_intro + '=', key
                )

    def __write_details(self, details):
        """
        Write out a file with all the details for a set of results.

        Raises OSError if there is a problem opening the file. We work with a
        copy of the details, from which we delete elements as they are
        printed. This allows us to print any remaining general information at
        the end, thus allowing arbitary information to be recorded.
        """
        fileh = open(
            os.path.join(self.__absdetailsdir, details.details_page()), 'w'
        )
        json_data = details.json_data_copy()
        self.__write_general_details(fileh, json_data)
        self.__write_platform_info(fileh, json_data)
        self.__write_tool_chain_info(fileh, json_data)
        self.__write_detailed_results(fileh, json_data)
        self.__write_other(fileh, json_data, '==', 'Other information')
        fileh.close()

    def write_all_details(self, result_set):
        """
        Write out all the details files for the supplied set of results
        """
        for res in result_set.results():
            self.__write_details(res.details())

    def write_table(self, title, result_set):
        """
        Given a list of results generate them as a mediawiki table, preceded
        by the supplied level 3 title
        """
        # The title, preceded and followed by a blank line
        self.__readme.writelines(f'\n=== {title} ===\n\n')

        # The wiki table header
        self.__wiki_tblhdr()

        # The wiki table body - one row for each entry
        for res in result_set.results():
            self.__wiki_tblrow(res)

        # The wiki table footer
        self.__wiki_tblftr()
