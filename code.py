# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2025 Sam Blenny
"""
This presents a menu on the serial port for reading, writing, or erasing the
initial bytes of an I2C FRAM chip. This is meant to be used with a TCA4307
hot-swap I2C buffer and a magnetic pogo pin connector on the I2C bus. The code
anticipates that the fram chip might appear or disappear at any time.
"""
from board import I2C
from adafruit_fram import FRAM_I2C


LIMIT = 32

MENU = f"""Menu:
 1  Read FRAM cart (print first {LIMIT} bytes)
 2  Write string to cart (limit {LIMIT} characters)
 3  Erase first {LIMIT} bytes (set to 0)
choice [1]: """

NO_CART_ERROR = "Unable to access FRAM"


def main():
    i2c = I2C()
    fram = None
    while True:
        n = input(MENU)
        try:
            if fram is None:
                fram = FRAM_I2C(i2c)
        except ValueError:
            print(NO_CART_ERROR)
            continue
        except OSError:
            print(NO_CART_ERROR)
            continue
        if n == "2":
            # Write to FRAM cart
            msg = input(f"what to write? (max {LIMIT} chars): ")
            clipped_msg = msg.encode()[:LIMIT]
            print("Writing...")
            try:
                fram[0:len(clipped_msg)] = clipped_msg
            except OSError:
                print(NO_CART_ERROR)
        elif n == "3":
            # Erase first bytes to 0
            print("Erasing...")
            try:
                for i in range(LIMIT):
                    fram[i] = 0
            except OSError:
                print(NO_CART_ERROR)
        # Always read the cart's header bytes
        try:
            print("Reading FRAM...")
            print(f"  len(fram) = {len(fram)}")
            print(f"  hex of first {LIMIT} bytes: ", fram[:LIMIT].hex())
        except OSError:
            print(NO_CART_ERROR)

main()
