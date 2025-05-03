# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2025 Sam Blenny

.PHONY: help bundle sync tty clean mount umount

# Name of top level folder in project bundle zip file should match repo name
PROJECT_DIR = $(shell basename `git rev-parse --show-toplevel`)

help:
	@echo "build project bundle:         make bundle"
	@echo "sync code to CIRCUITPY:       make sync"
	@echo "open serial terminal:         make tty"

# This is for use by .github/workflows/buildbundle.yml GitHub Actions workflow
bundle:
	@mkdir -p build
	python3 bundle_builder.py

# Sync current code and libraries to CIRCUITPY drive.
# This should work on macOS or Debian (see mount / umount targets below)
sync: bundle
	@if [ -d /Volumes/CIRCUITPY ]; then \
		xattr -cr build; \
		rsync -rcvO 'build/${PROJECT_DIR}/CircuitPython 9.x/' /Volumes/CIRCUITPY; \
		sync; fi
	@if [ -d /media/CIRCUITPY ]; then \
		rsync -rcvO 'build/${PROJECT_DIR}/CircuitPython 9.x/' /media/CIRCUITPY; \
		sync; fi

# Serial terminal: 115200 baud, no flow control (-fn)
# This should work on macOS or Debian
tty:
	if [ -d /dev/ttyACM0 ]; then \
		screen -fn /dev/ttyACM0 115200; \
	else \
		screen -fn /dev/tty.usbmodem* 115200; fi

clean:
	rm -rf build

# Mount CIRCUITPY from Debian command line
# You might need to do `sudo apt install pmount` before using this.
mount:
	@if [ ! -d /media/CIRCUITPY ] ; then \
		pmount `readlink -f /dev/disk/by-label/CIRCUITPY` CIRCUITPY; else \
		echo "/media/CIRCUITPY was already mounted"; fi

# Unmount CIRCUITPY from Debian command line.
# You might need to do `sudo apt install pmount` before using this.
umount:
	@if [ -d /media/CIRCUITPY ] ; then pumount CIRCUITPY; else \
		echo "/media/CIRCUITPY wasn't mounted"; fi
