import time
from RPi import GPIO

class i2c:
    def __init__(self,SDA,SCL,address=0b0100000):
        self.__sda = SDA
        self.__scl = SCL
        self.__address = address <<1

    def __setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.__sda,self.__scl], GPIO.OUT)
        GPIO.output(self.__sda,1)
        GPIO.output(self.__scl,1)
    def __start_conditie(self):
        # print('start')
        GPIO.output(self.__sda,0)
        GPIO.output(self.__scl,0)
    def __stop_conditie(self):
        # print('stop')
        GPIO.output(self.__scl,1)
        GPIO.output(self.__sda,1)


    def __write_bit(self,bit):
        # print('bit: %s'%bit)
        GPIO.output(self.__scl, 0)
        GPIO.output(self.__sda, bit)
        GPIO.output(self.__scl, 1)
        GPIO.output(self.__scl,0)
        GPIO.output(self.__sda,0)

    def __tick_scl(self):
        GPIO.output(self.__scl,0)
        GPIO.output(self.__scl,1)
        GPIO.output(self.__scl,0)

    def __ack(self):
        try:
            # GPIO.output(self.__sda, 0)
            GPIO.output(self.__scl,0)
            GPIO.setup(self.__sda, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.output(self.__scl,1)
            ack = GPIO.input(self.__sda)
            # print('ack: %s'%ack)
            GPIO.output(self.__scl, 0)
            return ack
        except Exception as ex:
            print(ex)
        finally:
            GPIO.setup([self.__sda, self.__scl], GPIO.OUT)


    def write_outputs(self,byte):
        try:
            self.__setup()
            self.__start_conditie()
            for i in reversed(range(8)):
                bit = (self.__address >> i) & 1
                self.__write_bit(bit)
            self.__ack()
            for i in range(8):
                bit = (byte >> i) & 1
                self.__write_bit(bit)
            self.__ack()
            self.__stop_conditie()
        except Exception as ex:
            print(ex)


    @staticmethod
    def zoek_adressen(sda,scl):
        try:
            result = []
            for i in range(8):
                zoek = i2c(sda, scl)
                address = 0b0100 <<3 | i
                address = address <<1
                zoek.__setup()
                zoek.__start_conditie()
                for i in reversed(range(8)):
                    bit = (address >> i) & 1
                    zoek.__write_bit(bit)
                ack = zoek.__ack()
                zoek.__stop_conditie()
                if ack != 1:
                    result.append(i)
            return result
        except Exception as ex:
            print(ex)