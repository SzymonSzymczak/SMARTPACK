import time
from RPi import GPIO
from model.mcp3008 import mcp3008
from model.lcd import lcd
mcp1 = mcp3008(0)
lcd1 = lcd(13, 19, 20, 21, 4, 17, 27, 22, 5, 6)


def setup():
    GPIO.setmode(GPIO.BCM)
    # GPIO.setup(12,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # GPIO.setup(18, GPIO.OUT)
    GPIO.setup([16,26], GPIO.OUT)
    time.sleep(1)

def a(pin):
    print('a')


try:
    setup()
    # GPIO.add_event_detect(12, GPIO.BOTH, callback=a, bouncetime=10)
    # while True:
    # #     time.sleep(0.5)
    GPIO.output(26,1)
    time.sleep(1)
    #     print(mcp1.read_data(0))
    #     time.sleep(1)
    #     print(GPIO.input(23))
    #     lcd1.send_message('haha')
        # print(GPIO.input(12))



# hier komt de loop

except KeyboardInterrupt:
    print('Bye')
except Exception as ex:
    print('Error!' + str(ex))
finally:
    GPIO.cleanup()
