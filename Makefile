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
	./process_results.py
	@mv README.md README.md.old
	@mv README-new.md README.md

# Get rid of old results
.PHONY: clean
clean:
	$(RM) README.md.old
	$(RM) README-new.md
	$(RM) README.pdf
	$(RM) README.html
