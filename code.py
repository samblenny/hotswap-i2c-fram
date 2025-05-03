# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2025 Sam Blenny
#
# This presents a menu on the serial port for reading, writing, or erasing the
# initial bytes of an I2C FRAM chip. This is meant to be used with two TCA4307
# hot-swap I2C buffers on channels 0 and 1 of a PCA9546A multiplexer. The
# buffers each go to a magnetic pogo pin connector. The code anticipates that
# the fram chip might appear or disappear at any time.
#
# Related Docs:
# - https://learn.adafruit.com/adafruit-pca9546-4-channel-stemma-qt-multiplexer
# - https://learn.adafruit.com/adafruit-tca4307
# - https://learn.adafruit.com/adafruit-i2c-fram-breakout
# - https://docs.circuitpython.org/projects/tca9548a/en/latest/
#
from board import STEMMA_I2C
from micropython import const
from adafruit_fram import FRAM_I2C
from adafruit_tca9548a import PCA9546A


LIMIT = const(64)
I2C_ADDR_FRAM = const(0x50)
I2C_ADDR_MUX = const(0x70)

MENU_2_SLOTS = f"""Menu:
 1  Scan for FRAM carts and print their header bytes
 2  Write message to slot 0 FRAM (max {LIMIT} bytes)
 3  Write message to slot 1 FRAM (max {LIMIT} bytes)
 4  Erase first {LIMIT} bytes (set to 0) of slot 0 FRAM
 5  Erase first {LIMIT} bytes (set to 0) of slot 1 FRAM
choice [1]: """

MENU_1_SLOT = f"""Menu:
 1  Print FRAM cart header bytes
 2  Write message to FRAM (max {LIMIT} bytes)
 3  Erase first {LIMIT} bytes of FRAM
choice [1]: """

NO_CART_ERROR = "Unable to access FRAM"

def hexdump(data):
    row_len = 16
    for row_start in range(0, len(data), row_len):
        hex_buf = []
        ascii_buf = []
        for b in data[row_start:row_start + row_len]:
            hex_buf.append('%02x' % b)
            ascii_buf.append(chr(b) if 32 <= b <= 127 else '.')
        if len(hex_buf) < row_len:
            hex_buf.append('  ' * row_len - len(hex_buf))
        print(' ', ' '.join(hex_buf), ' ', ''.join(ascii_buf))

def read(fram, start=0, end=LIMIT):
    # Read + hexdump a range of bytes from FRAM chip on selected mux channel.
    # This may raise exceptions if FRAM is not present or range not valid.
    hexdump(fram[start:end])

def write(fram):
    # Prompt for message and write it to an FRAM cart on selected mux channel
    # This may raise exceptions if FRAM is not present.
    msg = input(f"Message to write? (max {LIMIT} chars): ")
    clipped_msg = msg.encode()[:LIMIT]
    fram[0:len(clipped_msg)] = clipped_msg
    print("ok")

def erase(fram, start=0, end=LIMIT):
    # Erase a range of bytes of FRAM chip on selected mux channel
    for i in range(LIMIT):
        fram[i] = 0
    print("ok")

def mux_probe(mux_channel, addr):
    # Return true if device with address addr exists on specified mux channel
    present = False
    if mux_channel.try_lock():
        present = mux_channel.probe(addr)
        mux_channel.unlock()
    return present

def probe_without_mux(i2c, addr):
    # Return true if device with address addr exists on i2c bus
    present = False
    i2c.try_lock()
    try:
        i2c.writeto(addr, b'')
        present = True
    except OSError:
        pass
    finally:
        i2c.unlock()
    return present

def scan_slot(mux, channel):
    # Check for FRAM cart on selected channel, hexdump header bytes if found
    present = mux_probe(mux[channel], I2C_ADDR_FRAM)
    if not present:
        print(f"Slot {channel}: Empty")
    else:
        print(f"Slot {channel} fram_bytes[0:{LIMIT}]:")
        fram = FRAM_I2C(mux[channel])
        read(fram, 0, LIMIT)

def two_slot_main_loop(mux):
    while True:
        # Always start by scanning for carts and printing their header bytes
        print()
        scan_slot(mux, 0)
        print()
        scan_slot(mux, 1)
        print()
        # Show menu prompt and parse the response
        n = input(MENU_2_SLOTS)
        try:
            if n == "1":
                # Skip to next loop iteration to print the header bytes
                continue
            if n == "2":
                # Write to slot 0
                fram = FRAM_I2C(mux[0])
                write(fram)
            if n == "3":
                # Write to slot 1
                fram = FRAM_I2C(mux[1])
                write(fram)
            elif n == "4":
                # Erase slot 0
                fram = FRAM_I2C(mux[0])
                erase(fram)
            elif n == "5":
                # Erase slot 1
                fram = FRAM_I2C(mux[1])
                erase(fram)
        except OSError:
            print(NO_CART_ERROR)
        except ValueError:
            print(NO_CART_ERROR)

def one_slot_main_loop(i2c):
    while True:
        # Start by checking for cart and trying to print its header bytes
        print()
        if not probe_without_mux(i2c, I2C_ADDR_FRAM):
            print("Slot: Empty")
        else:
            try:
                fram = FRAM_I2C(i2c)
                print(f"fram_bytes[0:{LIMIT}]:")
                read(fram, 0, LIMIT)
            except ValueError as e:
                raise e
        print()
        # Show menu prompt and parse the response
        n = input(MENU_1_SLOT)
        try:
            if n == "1":
                # Skip to next loop iteration to print the header bytes
                continue
            if n == "2":
                # Write to FRAM
                if probe_without_mux(i2c, I2C_ADDR_FRAM):
                    fram = FRAM_I2C(i2c)
                    write(fram)
                else:
                    print(NO_CART_ERROR)
            elif n == "3":
                # Erase slot FRAM
                if probe_without_mux(i2c, I2C_ADDR_FRAM):
                    fram = FRAM_I2C(i2c)
                    erase(fram)
                else:
                    print(NO_CART_ERROR)
        except OSError:
            print(NO_CART_ERROR)
        except ValueError:
            print(NO_CART_ERROR)

def main():
    i2c = STEMMA_I2C()
    use_one_slot = False
    try:
        mux = PCA9546A(i2c)
        two_slot_main_loop(mux)
    except OSError as e:
        print("PCA9546A MUX NOT FOUND. STARTING IN ONE SLOT MODE.")
        print()
        use_one_slot = True
    if use_one_slot:
        one_slot_main_loop(i2c)

main()
