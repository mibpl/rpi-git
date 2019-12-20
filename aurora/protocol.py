
import json

class SetStateEvent:
    def __init__(self, light_map):
        self.light_map = light_map

    def serialize(self):
        return "SET " + json.dumps(self.light_map) + "\n"

    def deserialize(data):
        d = json.loads(data.strip())
        return SetStateEvent({int(k): v for k, v in d.items()})

def deserialize(message):
    event, data = message.split(' ', 1)
    if event == "SET":
        return SetStateEvent.deserialize(data)
    print("Bad event", event, data)