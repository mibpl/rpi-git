import socketserver
from led_config import LEDConfig
import protocol

use_fake_handler = False

lights = None
DARK = (0, 0, 0)
BLUE = (0, 0, 255)

def setup_board():
    global lights
    lights = neopixel.NeoPixel(board.D18, LEDConfig.total_lights, auto_write=False)
    lights.fill(DARK)

try:
    import board
    import neopixel
    setup_board()
except ImportError:
    print("!! Falling back to headless mode")
    use_fake_handler = True


class EventHandler(socketserver.StreamRequestHandler):
    def handle(self):
        print("Client connected")
        reader = self.rfile
        try:
            while True:
                data = reader.readline()
                if len(data) == 0:
                    break
                message = data.decode()
                print("Received", message)
                if not use_fake_handler:
                    self.on_message(message)
        finally:
            print("Client disconnected")

    def on_message(self, message):
        event = protocol.deserialize(message)
        if isinstance(event, protocol.SetStateEvent):
            lights.fill(DARK)
            for led, color in event.light_map.items():
                try:
                    lights[led] = color
                except IndexError as e:
                    print(e)
            lights.show()

class Server:
    def run(self):
        server = socketserver.TCPServer(('', 6666), EventHandler)
        server.serve_forever()

def main():
    server = Server()
    server.run()

if __name__ == '__main__':
    main()
