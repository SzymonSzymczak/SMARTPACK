class W1_temp_sensor:
    W1_PATH = '/sys/bus/w1/devices/{}/{}'
    def __init__(self, address):
        self.address = address

    def read_temp(self):
        filename = self.W1_PATH.format(self.address,'w1_slave')
        print('Trying to read {}'.format(filename))
        try:
            with open(filename, 'r') as file:
                for line in file:
                    position = line.find('t=')
                    if position > -1:
                        substr = line[position:]
                        t_str = substr[2:-1]
                        temp = int(t_str) /1000
                        return temp
        except IOError as ex:
            print('Failed to open {}'.format(ex))
if __name__ == '__main__':
    sensor = TempSensor('28-13debd116461')
    print('Het is: {}\N{DEGREE SIGN}C'.format(sensor.read_temp()))