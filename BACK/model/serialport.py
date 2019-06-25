import serial
class serialport:
    def __init__(self,par_port='/dev/ttyS0'):
        self.__port = par_port

    def send_message(self, message_in_bytes):
        try:
            ser = serial.Serial(self.__port,baudrate = 9600)
            ser.write(message_in_bytes)
            ser.close()
            return "message has been sent."
        except Exception as ex:
            print('Error: %s'%ex)
        finally:
            ser.close()

    def read_message(self,size_bytes, timeout):
        ser = serial.Serial(self.__port,timeout=timeout, baudrate = 9600)
        message = ''
        try:
            message = ser.read(size_bytes)
            return  str(message).lstrip('b\'').rstrip('\'')
        except Exception as ex:
            print('Error: %s'%ex)
        finally:
            ser.close()

