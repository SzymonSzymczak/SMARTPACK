# Imports
from flask import Flask, request, jsonify, json
import random
from flask_cors import CORS
from flask_socketio import SocketIO
from model.lcd import lcd
from model.mcp3008 import mcp3008
from RPi import GPIO
from smbus import SMBus
import time
import serial
import threading
import pynmea2
import datetime
from subprocess import check_output
from model.Database import Database

import math

trigger = 25
echo = 24
reed = 12
led = [16, 26]
led_w = 18
pull_sw = 23
lcd1 = lcd(13, 19, 20, 21, 4, 17, 27, 22, 5, 6)
gpsport = "/dev/ttyS0"
mcp1 = mcp3008()
ultrasonic_status = 'off'

Settings = {}

GPIO.setmode(GPIO.BCM)
GPIO.setup(trigger, GPIO.OUT)
GPIO.setup(led, GPIO.OUT)
GPIO.setup(led_w, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)
GPIO.setup(reed, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pull_sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)

status_pull = GPIO.input(pull_sw)
# Start app
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

conn = Database(app=app, user='mct', password='mct', db='Smartpack')
endpoint = '/api/v1'


@app.route('/')
def test():
    return jsonify('api')


@app.route('/api/ldr')
def ldr():
    waarde_ldr = mcp1.read_data(0)
    if waarde_ldr > 33000:
        waarde_ldr -= 33000
    waarde_ldr_procent = 100 - (waarde_ldr / 1023 * 100)
    print(waarde_ldr_procent)
    return jsonify(waarde_ldr_procent), 200


@app.route('/api/gpsdata')
def gpsdata():
    # data = conn.get_data('SELECT Latitude,Longitude,datetime from Smartpack.GpsDataHistory where date(Datetime) = CURDATE()')
    data = conn.get_data(
        'SELECT Latitude,Longitude,datetime,todaysRouteId,(Select count( Distinct todaysRouteId) from GpsDataHistory where date(DateTime) = curdate()) as countRouteId from Smartpack.GpsDataHistory where date(DateTime) = curdate() ORDER BY DateTime ASC')
    return jsonify(data), 200


@app.route('/api/savedroutes')
def savedroutes():
    data = conn.get_data('Select name,id,SavedRoutes.date as date from SavedRoutes')
    return jsonify(data), 200


@app.route('/api/savedroutes/<id>')
def savedroute(id):
    data = conn.get_data('Select Longitude,Latitude from GpsDataHistory where SavedRoutes_id = %s' % id)
    return jsonify(data), 200


@app.route('/api/settings')
def settings():
    get_settings()
    return jsonify(Settings), 200


@app.route('/api/init_statistics')
def init_statistics():
    data = conn.get_data('SELECT distinct DATE_FORMAT(datetime,"%Y-%m-%d") as dates from GpsDataHistory')
    return jsonify(data), 200


@app.route('/api/statistics', methods=['GET', 'POST'])
def get_stats():
    print(request.method)
    if request.method == 'POST':
        body = request.get_json()
        data = conn.get_data('Select Speed,DATE_FORMAT(DateTime,"%%Y-%%m-%%d %%H:%%i") as DateTime from GpsDataHistory where datetime between  %s " 00:00:00" and %s " 23:59:59"',
                             [body['dateFrom'], body['dateTo']])
        print(data)
        return jsonify(data),200


@socketio.on('changeSetting')
def changeSetting(data):
    x = conn.set_data("Update Settings set Value = %s where Setting = %s", [data[1], data[0]])
    get_settings()


@socketio.on('saveroute')
def saveroute(data):
    id = data[0]
    name = data[1]
    # print(id)
    check = conn.get_data(
        "Select SavedRoutes_id from GpsDataHistory where  date(DateTime) = curdate() and todaysRouteId = %s" % id)
    if check[0]['SavedRoutes_id'] == None:
        id_saved = conn.set_data('INSERT into SavedRoutes (name,date) VALUES ("%s",curdate())' % name)
        x = conn.set_data(
            'update GpsDataHistory set SavedRoutes_id = %s where date(DateTime) = curdate() and todaysRouteId = %s',
            [id_saved, id])
        socketio.emit('routesaved', {'savestatus': 1})
    else:
        socketio.emit('routesaved', {'savestatus': 0})


def reed_switch(pin):
    if (GPIO.input(reed) == 0) or Settings['Inside_light'] == 'off':
        GPIO.output(led_w, 0)
        print('reed on')
    elif Settings['Inside_light'] == 'on':
        GPIO.output(led_w, 1)
        print('reedoff')


def ultrasonic():
    time.sleep(0.12)
    status = 0
    global ultrasonic_status
    while True:

        # set Trigger to HIGH
        GPIO.output(trigger, True)

        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(trigger, False)
        time_start = time.time()
        StartTime = time.time()
        StopTime = time.time()

        # save StartTime
        while GPIO.input(echo) == 0 and time_start + 1 > time.time():
            StartTime = time.time()

        # save time of arrival
        while GPIO.input(echo) == 1:
            StopTime = time.time()

        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (TimeElapsed * 34300) / 2
        if 0 < distance < 10:
            if status != 'on':
                print('on')
                ultrasonic_status = 'on'
                status = 'on'
        elif status != 'off':
            ultrasonic_status = 'off'
            status = 'off'
            print('off')
        time.sleep(0.1)


def ip():
    while True:
        lcd1.clear()
        ips = check_output(['hostname', '--all-ip-addresses'])
        print('ips: %s' % ips)
        ip1 = str(ips).split(' ', 1)[-1].split(' ', 1)[0].lstrip('b\'')
        ip2 = str(ips).split(' ', 1)[0].split(' ', 1)[0].lstrip('b\'')
        # print('ip: %s' % ip)
        # lcd1.send_message(ip1)
        # lcd1.select_position(17)
        lcd1.send_message(ip2)
        time.sleep(10)


def gps():
    speed = 0
    time.sleep(0.1)
    data = 0
    added_id = 0
    last_track = time.time()
    latest_id = conn.get_data(
        "Select todaysRouteId,Latitude,Longitude from GpsDataHistory where date(Datetime) = curdate() ORDER BY DateTime Desc LIMIT 1;")
    print("data {}".format(latest_id))
    if str(latest_id) == '()':
        latest_id = 0
        prev_lon = 0
        prev_lat = 0
    else:
        prev_lat = latest_id[0]['Latitude']
        prev_lon = latest_id[0]['Longitude']
        latest_id = latest_id[0]['todaysRouteId']
    while 1:

        # print(latest_id)
        try:
            gpsport = "/dev/ttyS0"
            ser = serial.Serial(gpsport, baudrate=9600, timeout=0.5)
            data = ser.readline()
            # print(data)
            # print(str(data).lstrip('b\''))
        except Exception as ex:
            print("loading: %s" % ex)
            # time.sleep(0.001)
        # wait for the serial port to churn out data
        #     print(str(data).lstrip('b\'')[0:6])
        #     print('ddd')
        if Settings['GPS'] == 'on':
            # print('not stopped')
            if str(data).find(
                    'GPGGA') != -1:  # the long and lat data are always contained in the GPGGA string of the NMEA data
                # print('data')
                try:
                    msg = pynmea2.parse(str(data).lstrip('b\'').rstrip('\\r\\n\''))
                    # parse the latitude and print
                    latval = msg.latitude
                    long = msg.longitude
                    qual = msg.gps_qual
                    sats = msg.num_sats
                    acc = float(msg.horizontal_dil)
                    print(acc)
                    lat = latval
                    lon = long
                    # socketio.emit('gps',
                    # {'lat': str(latval), 'long': str(long), 'quality': str(qual), 'numSats': str(sats)})
                    try:
                        speed = float(speed)
                    except:
                        speed = 0
                    if (abs(prev_lat - lat) > 0.0003 or abs(prev_lon - long) > 0.0003) and (
                            qual != 0) and (acc < 5) and Settings['GPS'] == 'on':
                        prev_lat = lat
                        prev_lon = lon
                        if (last_track + 1800) > time.time():
                            added_id = 0
                            conn.set_data(
                                'INSERT into Smartpack.GpsDataHistory(dateTime,Longitude,LAtitude,Speed,todaysRouteId) VALUES (%s,%s,%s,%s,%s)',
                                [str(
                                    datetime.datetime.now()), str(lon), str(lat), str(speed), latest_id])
                            last_track = time.time()
                        elif added_id == 0:
                            latest_id += 1
                            added_id = 1
                            conn.set_data(
                                'INSERT into Smartpack.GpsDataHistory(dateTime,Longitude,LAtitude,Speed,todaysRouteId) VALUES (%s,%s,%s,%s,%s)',
                                [str(
                                    datetime.datetime.now()), str(lon), str(lat), str(speed), latest_id])
                            last_track = time.time()

                except Exception as ex:
                    print(ex)
            elif str(data).find('GPVTG') != -1:
                data = str(data).lstrip('b\'').rstrip('\\r\\n\'')
                speedVal = data[data.find('N') + 2:data.find('K') - 1]
                # print('Speed: {}'.format(speedVal))
                speed = speedVal


def check_statuses():
    time_wait = 5
    time_on = time.time() - time_wait
    noted_d = 0
    noted_l = 0
    time_noted_d = 99999999999999999999999999
    time_noted_l = 99999999999999999999999999
    status_ldr = 0
    status_ldr = 'light'

    while True:
        # print(GPIO.input(pull_sw))
        try:
            waarde_ldr = mcp1.read_data(0)
            # if waarde_ldr > 3200:
            #     waarde_ldr -= 3200
            # elif waarde_ldr > 1024 or waarde_ldr < 0:
            #     waarde_ldr = 0
            waarde_ldr_procent = 100 - (waarde_ldr / 1023 * 100)
            # print(waarde_ldr)
            print(waarde_ldr_procent)
            time.sleep(0.5)
            # waarde_ldr_procent = 0
        except Exception as ex:
            print(ex)
            # pass

        if waarde_ldr_procent < 23:
            if noted_d == 0:
                noted_d = 1
                time_noted_d = time.time()
            elif noted_d == 1 and time_noted_d+10 < time.time():
                status_ldr = 'night'
                noted_l = 0

        elif waarde_ldr_procent > 30:
            if noted_l == 0:
                noted_l = 1
                time_noted_l = time.time()
            elif noted_l == 1 and time_noted_l+10 < time.time():
                status_ldr = 'light'
                noted_d = 0
        # print(waarde_ldr_procent)
        # print(status_ldr)
        print(status_ldr)
        if (GPIO.input(pull_sw) == 0 and ultrasonic_status == 'on' and status_ldr == 'night' and Settings[
            'Auto_light'] == 'on') or (time.time() < time_on + time_wait):
            if GPIO.input(pull_sw) == 0 and ultrasonic_status == 'on' and status_ldr == 'night':
                time_on = time.time()
                # print(Settings['Light_mode'])
            if Settings['Light_mode'] == 'static':
                GPIO.output(led, 1)
            elif Settings['Light_mode'] == 'blink':
                GPIO.output(led, 0)
                time.sleep(0.5)
                GPIO.output(led, 1)
                time.sleep(0.5)
            elif Settings['Light_mode'] == 'special':
                GPIO.output(led[0], 0)
                GPIO.output(led[1], 1)
                time.sleep(0.5)
                GPIO.output(led[0], 1)
                GPIO.output(led[1], 0)
                time.sleep(0.5)

        elif time.time() > time_on + time_wait:
            GPIO.output(led, 0)


def get_settings():
    data = conn.get_data("Select * from Settings")
    for dict in data:
        Settings[dict['Setting']] = dict['Value']
    print(Settings)


get_settings()
# ip()
ultra = threading.Thread(target=ultrasonic)
statuses = threading.Thread(target=check_statuses)
ip = threading.Thread(target=ip)
ip.start()
ultra.start()
statuses.start()
gpsT = threading.Thread(target=gps)
gpsT.start()
GPIO.add_event_detect(reed, GPIO.BOTH, callback=reed_switch, bouncetime=100)
# GPIO.add_event_detect(pull_sw, GPIO.BOTH, callback=pull_switch, bouncetime=300)
# Start app
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=0)
