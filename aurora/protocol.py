
import json

class SetStateEvent:
    def __init__(self, light_map):
        self.light_map = light_map

    def serialize(self):
        return "SET " + json.dumps(self.light_map)

    def deserialize(data):
        return SetStateEvent(json.loads(data.strip()))

def deserialize(message):
    event, data = message.split(' ', 1)
    if event == "SET":
        return SetStateEvent.deserialize(data)