import time
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusIOException

# Initialize the client (RTU mode)
client = ModbusSerialClient(
    method='rtu',
    port='/dev/ttyUSB0',     # Or 'COM3' on Windows
    baudrate=9600,
    stopbits=1,
    bytesize=8,
    parity='N',
    timeout=1
)


MODBUS_ID = 255  # default address
REGISTER = 0x0000

# Connect to the Modbus network
if not client.connect():
    print("Failed to connect to Modbus slave.")
    exit(1)

"""
# Example: Read 1 coil (digital output) from slave at address 1, coil #0
for device in range(255, 256):
    print(device)
    result = client.read_holding_registers(address=0, count=1, slave=device)
    if not isinstance(result, ModbusIOException):
        print(device, result)        

        """

DEVICE_ID = 5

result = client.read_holding_registers(address=1,slave=DEVICE_ID)
print(result)

result= client.read_exception_status(slave=DEVICE_ID)
print(result)

result=client.read_coils(address=1000, slave=DEVICE_ID)
print(result)


"""
result = client.write_coil(address=0, slave=DEVICE_ID, value=0)
time.sleep(1)
result = client.write_coil(address=0, slave=DEVICE_ID, value=1)
time.sleep(1)
result = client.write_coil(address=0, slave=DEVICE_ID, value=0)
# result = client.read_holding_registers(address=REGISTER, count=1, slave=MODBUS_ID)


result = client.read_holding_registers(address=0,count=1,slave=5)

# result = client.write_register(address=0,value=5,slave=255)
"""

print(result)

# Disconnect cleanly
client.close()
