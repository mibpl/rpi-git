# -*- coding: utf-8 -*-

import logging
import time

import cflib.crtp
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

logging.basicConfig(level=logging.INFO)

URI = 'radio://0/80/250K'

# send_hover_setpoint vx vy yawrate zdistance
class MibCommander(object):
    def __init__(self, cf):
        self.cf = cf
        self.cmd = cf.commander

    def ascend(self):
        for y in range(10):
            self.cmd.send_hover_setpoint(0, 0, 0, y / 25)
            time.sleep(0.1)

    def descend(self):
        for y in range(10):
            self.cmd.send_hover_setpoint(0, 0, 0, (10 - y) / 25)
            time.sleep(0.1)

    def wait_in_place(self):
        for _ in range(20):
            self.cmd.send_hover_setpoint(0, 0, 0, 0.4)
            time.sleep(0.1)

    def smooth_right(self):
        for _ in range(25):
            self.cmd.send_hover_setpoint(0.5, 0, 36, 0.4)
            time.sleep(0.1)

    def smooth_left(self):
        for _ in range(25):
            self.cmd.send_hover_setpoint(0.5, 0, -36, 0.4)
            time.sleep(0.1)

    def forward(self):
        for _ in range(5):
            self.cmd.send_hover_setpoint(0.5, 0, 0, 0.4)
            time.sleep(0.1)

    def living_room_table_correction_right(self):
        for _ in range(2):
            self.cmd.send_hover_setpoint(0.5, 0, 36, 0.4)
            time.sleep(0.1)
        for _ in range(2):
            self.cmd.send_hover_setpoint(0.5, 0, 0, 0.4)
            time.sleep(0.1)

    def rotate_in_place(self):
        for _ in range(25):
            self.cmd.send_hover_setpoint(0, 0, -36, 0.4)
            time.sleep(0.1)


if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)

    with SyncCrazyflie(URI) as scf:
        print("Executing sequence")
        cf = scf.cf

        cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(0.1)
        cf.param.set_value('kalman.resetEstimation', '0')
        time.sleep(2)

        mib = MibCommander(cf)

        mib.ascend()

        mib.wait_in_place()

        for _ in range(9):
            mib.forward()

        mib.smooth_left()

        for _ in range(4):
            mib.forward()

        #mib.living_room_table_correction_right()

        for _ in range(11):
            mib.forward()

        mib.smooth_right()
        mib.smooth_left()

        mib.wait_in_place()
        mib.wait_in_place()

        mib.descend()
