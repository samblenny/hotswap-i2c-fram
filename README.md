<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: Copyright 2025 Sam Blenny -->
# Hot-Swap I2C FRAM

![shell interiors](shell-interiors.jpeg)

![base-with-carts](base-with-carts.jpeg)

This repo has code and design files for a hot-swappable I2C FRAM memory
cartridges meant for use with the TCA4307 hot-swap I2C buffer and PCA9546 I2C
multiplexer.

Related guide:
[I2C FRAM Memory Carts](https://adafruit-playground.com/u/SamBlenny/pages/i2c-fram-memory-carts)

Designed the cart shell with Blender 4.4 using lots of geometry node modifiers.
For STL, .3mf, and .blend files, check out `fram-cart-shell-*` in the top level
of this repo.

CircuitPython Library dependencies (see bundle_manifest.cfg):
- adafruit_bus_device
- adafruit_fram


