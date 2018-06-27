#!/usr/bin/env python
# ------------------------------------------------------
#
# This is a program for PCF8591 Module.
#
# Warnng! The Analog input MUST NOT be over 3.3V!
#    
# In this script, we use a poteniometer for analog
# input, and a LED on AO for analog output.
#
# you can import this script to another by:
# import PCF8591 as ADC
#
# ADC.Setup(Address)  # Check it by sudo i2cdetect -y -1
# ADC.read(channal)	# Channal range from 0 to 3
# ADC.write(Value)	# Value range from 0 to 255
#
# ------------------------------------------------------
import smbus

# for RPI version 1, use "bus = smbus.SMBus(0)"
bus = smbus.SMBus(1)


def read(channel, address=0x48):  # channel
    try:
        if channel == 0:
            bus.write_byte(address, 0x40)
        if channel == 1:
            bus.write_byte(address, 0x41)
        if channel == 2:
            bus.write_byte(address, 0x42)
        if channel == 3:
            bus.write_byte(address, 0x43)
        bus.read_byte(address)  # dummy read to start conversion
    except Exception as e:
        print("Address: %s" % address)
        print(e)
    return bus.read_byte(address)


def write(value, address=0x48):
    try:
        temp = value  # move string value to temp
        temp = int(temp)  # change string to integer
        # print temp to see on terminal else comment out
        bus.write_byte_data(address, 0x40, temp)
    except Exception as e:
        print("Error: Device address: 0x%2X" % address)
        print(e)


if __name__ == "__main__":
    while True:
        print('AIN0 = ', read(0))
        print('AIN1 = ', read(1))
        tmp = read(0)
        tmp = tmp * (255 - 125) / 255 + 125  # LED won't light up below 125, so convert '0-255' to '125-255'
        write(tmp)
