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

# Connect to the Modbus network
if not client.connect():
    print("Failed to connect to Modbus slave.")
    exit(1)

# Example: Read 1 coil (digital output) from slave at address 1, coil #0
try:
    result = client.read_coils(address=1, count=1, slave=1)
    print(result)
    if not result.isError():
        print(f"Coil 0 state: {result.bits[0]}")
    else:
        print(f"Read error: {result}")
except ModbusIOException as e:
    print(f"IO exception: {e}")



# example: write a single coil (turn on relay)
result = client.write_coil(address=5, value=True, slave=1)
if not result.isError():
    print("coil successfully written.")
else:
    print(f"write error: {result}")



time.sleep(2)

# example: write a single coil (turn on relay)
result = client.write_coil(address=5, value=False, slave=1)
if not result.isError():
    print("coil successfully written.")
else:
    print(f"write error: {result}")

# Disconnect cleanly
client.close()
