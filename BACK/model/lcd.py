from RPi import GPIO
import time
short_delay = 0.0001
long_delay = 1

class lcd:

    def __init__(self,e=20,rs=21,db7=19,db6=13,db5=6,db4=5,db3=22,db2=27,db1=17,db0=18):
        self.__e = e
        self.__rs = rs
        self.__list_db = [db0,db1,db2,db3,db4,db5,db6,db7]
        self.__init_GPIO()
        self.init_LCD()


    def __init_GPIO(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__list_db, GPIO.OUT)
        GPIO.setup([self.__e, self.__rs],GPIO.OUT)

    def init_LCD(self):
        self.send_instruction(0b00111000)
        self.send_instruction(0b00001111)
        self.send_instruction(0b00000001)

    def set_data_bits(self,byte):
        for i in range(8):
            GPIO.output(self.__list_db[i], 0)
        for i in range(8):
            bit = byte >> i & 1
            # print(bit)
            GPIO.output(self.__list_db[i], bit)


    def send_instruction(self,data_byte):
        GPIO.output(self.__e, 1)
        GPIO.output(self.__rs,0)
        self.set_data_bits(data_byte)
        GPIO.output(self.__e, 0)
        time.sleep(short_delay)

    def send_character(self,data_byte):
        GPIO.output(self.__e, 1)
        GPIO.output(self.__rs,1)
        self.set_data_bits(data_byte)
        GPIO.output(self.__e, 0)
        time.sleep(short_delay)

    def second_row(self):
        self.send_instruction(0b11000000)


    def send_message(self,message):
        teller = 0
        for k in message:
            # print(bin(ord(k)))
            if teller == 16:
                self.second_row()
                self.send_character(ord(k))
                teller += 1
            elif teller == 32:
                time.sleep(long_delay)
                self.clear()
                self.send_character(ord(k))
                teller = 0
            else:
                self.send_character(ord(k))
                teller += 1

    def clear(self):
        self.send_instruction(0b00000001)

    def select_position(self,position):
        position = int(position)
        if position <= 16:
            instruction = 0b10000000 | (position -1)
            self.send_instruction(instruction)
        elif 32 >= position > 16:
            position += 64 -17
            instruction = 0b10000000 | position
            self.send_instruction(instruction)
        else:
            print('Geen geldige positie')



