import serial

# Convert hex string to bytes
raw_request = bytes.fromhex("00 03 00 03 00 01")

# Replace with your actual serial port
SERIAL_PORT = '/dev/ttyUSB0'  # or 'COM3' on Windows

# http://www.chinalctech.com/m/view.php?aid=454

def append_modbus_crc(data: bytes) -> bytes:
    """
    Appends Modbus RTU CRC-16 to a message.
    Returns the original data + 2 CRC bytes (little endian).
    """
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            lsb = crc & 0x0001
            crc >>= 1
            if lsb:
                crc ^= 0xA001  # Modbus CRC polynomial

    crc_low = crc & 0xFF
    crc_high = (crc >> 8) & 0xFF
    return data + bytes([crc_low, crc_high])


# Open the serial port
ser = serial.Serial(
    port=SERIAL_PORT,
    baudrate=9600,
    bytesize=8,
    parity='N',
    stopbits=1,
    timeout=1
)

request = append_modbus_crc(raw_request)

print(request.hex())

# Send the raw Modbus frame
ser.write(request)
print("✅ Sent request")

# Read response (you may need to adjust size and timing)
response = ser.read(32)  # Expected: [address, function, byte count, data_hi, data_lo, crc_lo, crc_hi]
print("📥 Raw response:", response.hex())

ser.close()
