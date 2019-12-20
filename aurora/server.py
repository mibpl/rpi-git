import asyncio
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

class EventHandler:
    def __init__(self):
        self.lights = None

    def setup_board(self):
        self.lights = neopixel.NeoPixel(board.D18, LEDConfig.total_lights, auto_write=False)
        self.lights.fill(DARK)

    async def on_message(self, message):
        if self.lights is None:
            self.setup_boards()

        event = protocol.deserialize(message)
        if isinstance(event, protocol.SetStateEvent):
            self.lights.fill(DARK)
            for led, color in event.leds:
                self.lights[led] = color
            self.lights.show()

class Server:
    def __init__(self):
        self.handler = EventHandler()

    async def on_connect(self, reader, writer):
        print("Client connected")
        while not reader.at_eof():
            data = await reader.readline()
            message = data.decode()
            print(f"Received {message}")
            if not use_fake_handler:
                await self.handler.on_message(message)
        print("Client disconnected")

    async def run(self):
        server = await asyncio.start_server(
            self.on_connect, '', 6666)

        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        async with server:
            await server.serve_forever()

async def main():
    server = Server()
    await server.run()

asyncio.run(main())