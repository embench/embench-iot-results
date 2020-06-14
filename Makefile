# Makefile to drive collation of benchmark results

# Copyright (C) 2019 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

# Update the README file
.PHONY: results
results:
	./process_results.py --resdir results

# Get rid of old results
.PHONY: clean
clean:
	$(RM) README.mediawiki
	$(RM) details/*.mediawiki
