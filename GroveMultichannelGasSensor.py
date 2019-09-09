# !/usr/bin/env python
import time
import sys
from enum import Enum

import RPi.GPIO as GPIO
import smbus

# use the bus that matches your raspi version
bus = smbus.SMBus(3)


class GasType(Enum):
    CO = 0
    NO2 = 1
    NH3 = 2
    C3H8 = 3
    C4H10 = 4
    CH4 = 5
    H2 = 6
    C2H5OH = 7


class MultichannelGasSensor:
    address = None
    is_connected = False
    res = [0] * 3
    res0 = [0] * 3
    version = 1

    def __init__(self, address=0x04):
        self.address = address
        self.is_connected = False
        self.power_on()
        self.calibrate()
        time.sleep(5)
        if self.read_r0() >= 0:
            print("Gas sensor connected")
            self.is_connected = True
        self.version = self.get_version()

    def get_version(self):
        # if self.get_addr_dta(6, 0) == 1126:
        #     return 2
        return 1

    def power_on(self):
        if self.version == 1:
            self.send_i2c(0x21)
        elif self.version == 2:
            dta_test = []
            dta_test[0] = 11
            dta_test[1] = 1
            self.send_i2c_multiple(dta_test, 2)

    def power_off(self):
        if self.version == 1:
            self.send_i2c(0x20)
        elif self.version == 2:
            dta_test = []
            dta_test[0] = 11
            dta_test[1] = 0
            self.send_i2c_multiple(dta_test, 2)

    def measure_CO(self):
        return self.calc_gas(GasType.CO)

    def measure_NO2(self):
        return self.calc_gas(GasType.NO2)

    def measure_NH3(self):
        return self.calc_gas(GasType.NH3)

    def measure_C3H8(self):
        return self.calc_gas(GasType.C3H8)

    def measure_C4H10(self):
        return self.calc_gas(GasType.C4H10)

    def measure_CH4(self):
        return self.calc_gas(GasType.CH4)

    def measure_H2(self):
        return self.calc_gas(GasType.H2)

    def measure_C2H5OH(self):
        return self.calc_gas(GasType.C2H5OH)

    def calc_gas(self, gas_type):
        if self.version == 1:
            if not self.is_connected:
                if self.read_r0() >= 0:
                    self.is_connected = True
                else:
                    return -1.0

            if self.read_resistance() < 0:
                return -2.0

            ratio0 = self.res[0] / self.res0[0]
            ratio1 = self.res[1] / self.res0[1]
            ratio2 = self.res[2] / self.res0[2]
        if self.version == 2:
            self.led_on()
            # int A0_0 = get_addr_dta(6, ADDR_USER_ADC_HN3);
            # int A0_1 = get_addr_dta(6, ADDR_USER_ADC_CO);
            # int A0_2 = get_addr_dta(6, ADDR_USER_ADC_NO2);
            #
            # int An_0 = get_addr_dta(CH_VALUE_NH3);
            # int An_1 = get_addr_dta(CH_VALUE_CO);
            # int An_2 = get_addr_dta(CH_VALUE_NO2);
            #
            # ratio0 = An_0/A0_0*(1023.0-A0_0)/(1023.0-An_0);
            # ratio1 = An_1/A0_1*(1023.0-A0_1)/(1023.0-An_1);
            # ratio2 = An_2/A0_2*(1023.0-A0_2)/(1023.0-An_2);

        c = 0

        if gas_type is GasType.CO:
            c = (ratio1 ** -1.179) * 4.385

        if gas_type is GasType.NO2:
            c = (ratio2 ** 1.007) / 6.855

        if gas_type is GasType.NH3:
            c = (ratio0 ** -1.67) * 1.47

        if gas_type is GasType.C3H8:
            c = (ratio0 ** -2.518) * 570.164

        if gas_type is GasType.C4H10:
            c = (ratio0 ** -2.138) * 398.107

        if gas_type is GasType.CH4:
            c = (ratio1 ** --4.363) * 630.957

        if gas_type is GasType.H2:
            c = (ratio1 ** -1.8) * 0.73

        if gas_type is GasType.C2H5OH:
            c = (ratio1 ** -1.552) * 1.622

        if self.version == 2:
            self.led_off()

        if self.is_number(c):
            return c
        return -3

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def led_on(self):
        dta_test = []
        dta_test[0] = 10
        dta_test[1] = 1
        self.send_i2c_multiple(dta_test, 2)

    def led_off(self):
        dta_test = []
        dta_test[0] = 10
        dta_test[1] = 0
        self.send_i2c_multiple(dta_test, 2)

    def read_r0(self):
        rtn_data = 0

        rtn_data = self.read_data(0x11)
        if rtn_data > 0:
            self.res0[0] = rtn_data
        else:
            print("Can't read from 0x11: " + str(rtn_data))
            return rtn_data  # unsuccessful

        rtn_data = self.read_data(0x12)
        if rtn_data > 0:
            self.res0[1] = rtn_data
        else:
            print("Can't read from 0x12: " + str(rtn_data))
            return rtn_data  # unsuccessful

        rtn_data = self.read_data(0x13)
        if rtn_data > 0:
            self.res0[2] = rtn_data
        else:
            print("Can't read from 0x13: " + str(rtn_data))
            return rtn_data  # unsuccessful

        return 1

    def read_resistance(self):
        rtn_data = 0

        rtn_data = self.read_data(0x01)
        if rtn_data >= 0:
            self.res[0] = rtn_data
        else:
            print("Can't read from 0x01: " + str(rtn_data))
            return rtn_data  # unsuccessful

        rtn_data = self.read_data(0x02)
        if rtn_data >= 0:
            self.res[1] = rtn_data
        else:
            print("Can't read from 0x02: " + str(rtn_data))
            return rtn_data  # unsuccessful

        rtn_data = self.read_data(0x03)
        if rtn_data >= 0:
            self.res[2] = rtn_data
        else:
            print("Can't read from 0x03: " + str(rtn_data))
            return rtn_data  # unsuccessful

        return 0

    def read_data(self, cmd):
        buffer = [0] * 4
        checksum = 0
        rtn_data = 0

        buffer = bus.read_i2c_block_data(self.address, cmd, 4)

        checksum = buffer[0] + buffer[1] + buffer[2]
        print(str(buffer[0]) + " + " + str(buffer[1]) + " + " + str(buffer[2]) + " = " + str(checksum) + " ? " + str(buffer[3]))
        if checksum != buffer[3]:
            return -4
        rtn_data = (buffer[1] << 8) + buffer[2]

        return rtn_data

    def send_i2c(self, cmd):
        bus.write_byte(self.address, cmd)

    def send_i2c_multiple(self, dta, dta_length):
        for i in range(dta_length):
            self.send_i2c(dta[i])

    def calibrate(self):
        if self.version == 1:
            self.send_i2c(0x22)
            if not self.read_r0():
                time.sleep(5)
                self.calibrate()
        elif self.version == 2:
            pass

    # def get_addr_dta(self, addr_reg, dta):
    #     self.send_i2c(addr_reg)
    #     self.send_i2c(dta)
    #     time.sleep(2)
    #     read_data = self.read_data(2)
    #
    #     data = 0
    #     raw = []
    #     count = 0
