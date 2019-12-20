import socketserver
from led_config import LEDConfig
import protocol

use_fake_handler = False

try:
    import board
    import neopixel
except ImportError:
    use_fake_handler = True

DARK = (0, 0, 0)
BLUE = (0, 0, 255)

class EventHandler(socketserver.StreamRequestHandler):
    def __init__(self, *args):
        super().__init__(*args)
        print("Handler created", args)
        self.lights = None

    def setup_board(self):
        self.lights = neopixel.NeoPixel(board.D18, LEDConfig.total_lights, auto_write=False)
        self.lights.fill(DARK)

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
                    self.handler.on_message(message)
        finally:
            print("Client disconnected")

    def on_message(self, message):
        if self.lights is None:
            self.setup_boards()

        event = protocol.deserialize(message)
        if isinstance(event, protocol.SetStateEvent):
            self.lights.fill(DARK)
            for led, color in event.leds:
                self.lights[led] = color
            self.lights.show()

class Server:
    def run(self):
        server = socketserver.TCPServer(('', 6666), EventHandler)
        server.serve_forever()

def main():
    server = Server()
    server.run()

if __name__ == '__main__':
    main()