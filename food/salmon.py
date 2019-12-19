import os
import sys
import time
import logging
import random
from pyrrd.rrd import DataSource, RRA, RRD
from pyrrd.graph import DEF, CDEF, VDEF, LINE, AREA, GPRINT, Graph
import rrdtool
import sensors
import RPi.GPIO as GPIO

TARGET = 62.8
rrd_path = '/tmp/'
graphfile = '/tmp/rrdgraph'

logging.basicConfig(
    level=logging.DEBUG,
    format='\r%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M'
)


def rrd_fn(name):
    return rrd_path + name + ".rrd"


def ts():
    return int(time.time())


def maybeCreateRRD(name, devs):
    filename = rrd_fn(name)
    if os.path.isfile(filename):
        logging.info("RRD already present: %s", name)
        return
   
    rrdtool.create(*(
        [filename, '--step', '2'] +
        ['DS:'+dev+':GAUGE:5:U:U' for dev in devs] +
        ['RRA:AVERAGE:0.5:1:' + str(1024**2)]
    ))
        
    logging.info("RRD created")


def render(rrd, devs, time_window_sec=30*60):
    palette = [
        '#00ffff', '#0080ff', '#0000ff'
    ]
    dev2color = dict(zip(devs, palette))
    statements = [
        LINE(value=str(TARGET), color='#990000', legend='Target')
    ]
    for dev in devs:
        df = DEF(rrdfile=rrd.filename, vname=dev, dsName=dev)
        statements.append(df)
        statements.append(
            LINE(defObj=df, color=dev2color[dev], legend=dev)
        )
    
    now = ts()
    g = Graph(
        graphfile + "-" + str(time_window_sec) + ".png", 
        start=now-time_window_sec,
        end=now+10,
        vertical_label='C'
    )
    g.data.extend(statements)
    g.write()


last_burn_status = False


def update_burn(desired):
    global last_burn_status
    if last_burn_status != desired:
        logging.info("Burn status set to: " + str(desired))
    last_burn_status = desired
    if desired:
        GPIO.output(24, 1)
    else:
        GPIO.output(24, 0)


def panic(burn):
    logging.error("Panic! Powering down.")
    update_burn(burn, False)



def update_prompt(r, avg):
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    avg = '\033[32m%05.2f\033[39m' % avg
    r = "\033[39m   SNR\033[36m " + ' '.join([
        '%05.2f' % x for x in r
    ])
    burn = "   BRN\033[31m " + str(last_burn_status).ljust(6, ' ')
    s = "\033[90m" + t + "\033[39m   AVG " + avg + burn + r
    sys.stdout.write('\r' + s + '\033[39m')
    sys.stdout.flush()


def burn_setup():
    GPIO.setmode(GPIO.BCM) 
    GPIO.setup(23, GPIO.OUT)
    GPIO.setup(24, GPIO.OUT)
    GPIO.output(23, 0)
    GPIO.output(24, 0)


def start_read():
    GPIO.output(23, 1)


def end_read():
    GPIO.output(23, 0)


def main():
    with open('data/medium.txt', 'r') as f:
        print('\033[91m')
        print(f.read())
        print('\033[0m')

    print('       \033[94mSalMon \033[92mv0.1\033[0m')
    print('')

    devs = sorted(sensors.find_sensors())
    if len(devs) != 3:
        logging.critical("Missing sensors!")
        return

    logging.warning("Sensors: %s", ' '.join(devs))
    rrd_name = '_'.join(devs)

    maybeCreateRRD(rrd_name, devs)
    rrd = RRD(rrd_fn(rrd_name))

    main_sleep = 0.2
    hystheresis = 1.0

    burn_setup()
    global last_burn_status


    while True:
        start_read()
        readings = [
            sensors.read_sensor(dev) for dev in devs
        ]
        end_read()
        sreadings = ':'.join(map(str, readings))

        if None in readings:
            logging.error("No reading: " + sreadings)
            panic()
            continue

        avg = sum(readings) / len(readings)
        if last_burn_status:
            burn_new = avg < TARGET + hystheresis / 2.0
        else:
            burn_new = avg < TARGET - hystheresis / 2.0
        update_burn(burn_new)

        update_prompt(readings, avg)

        now = ts()
        rrd.bufferValue(now, sreadings)
        rrd.update()
        render(rrd, devs)
        render(rrd, devs, 60*60)
        render(rrd, devs, 2*60*60)
        render(rrd, devs, 4*60*60)

        time.sleep(main_sleep)

try:
    main()
except:
    GPIO.cleanup()
    raise
