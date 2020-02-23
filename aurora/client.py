import socket
import sys

def connect():
    for host in [
        '192.168.1.183',
        '127.0.0.1'
    ]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, 6666))
            return s
        except Exception as e:
            print(f"Connection to {host} failed: {e}")
    raise Exception("No server found")