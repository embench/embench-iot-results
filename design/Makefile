# Makefile to process PlantUML to SVG

# Copyright (C) 2020 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

# Update the README file

.PHONY: all
all: plantuml class-diagram.svg

.PHONY: plantuml
plantuml:
	@if ! which plantuml > /dev/null; \
	then \
	    false; \
	fi

class-diagram.svg: class-diagram.txt
	plantuml -tsvg $^

# Blow away old result
.PHONY: clean
	$(RM) class-diagram.svg
