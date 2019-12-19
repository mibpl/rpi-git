import re

dev_base_path = '/sys/devices/w1_bus_master1/'

def read_sensor(dev):
    path = dev_base_path + dev + '/w1_slave'
    with open(path, 'r') as f:
        lines = f.readlines()
        if lines[0].strip()[-3:] != 'YES':
            return None
        s = re.search('t=(\d+)', lines[1]).group(1)
        return int(s) / 1000.0

slaves_list_path = '/sys/devices/w1_bus_master1/w1_master_slaves'

def find_sensors():
    with open(slaves_list_path, 'r') as f:
        return [x.strip() for x in f.readlines()]

#print find_sensors()

#print read_sensor("/sys/devices/w1_bus_master1/28-051670c670ff/w1_slave")
