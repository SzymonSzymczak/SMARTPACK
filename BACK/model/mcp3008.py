import spidev

spi = spidev.SpiDev()
channels = [10000000,10010000,10100000,10110000,11000000,11010000,11100000,11110000]


class mcp3008:
    def __init__(self, par_ce_waarde=0, par_clockspeed=(10 ** 2)):
        self.__ce = par_ce_waarde
        self.__clockspeed = par_clockspeed

    @property
    def ce(self):
        return self.__ce

    @ce.setter
    def ce(self, value):
        self.__ce = value

    @property
    def colckspeed(self):
        return self.__clockspeed

    @colckspeed.setter
    def colckspeed(self, value):
        self.__clockspeed = value

    def read_data(self, channel):
        try:
            spi.open(0, self.__ce)
            spi.max_speed_hz = self.__clockspeed
            list_result = spi.xfer2([0b00000001,channels[channel],0])
            spi.close()
            # print(list_result)
            byte2 = list_result[1]
            # print(bin(byte2))
            byte3 = (list_result[2] | 0b00000000)
            # print(bin(byte3))
            result = (byte2 & 0b00000011) <<8 | byte3
            result = result | byte2
            return result
        except Exception as ex:
            print("Fout: " + ex)
        finally:
            spi.close()
