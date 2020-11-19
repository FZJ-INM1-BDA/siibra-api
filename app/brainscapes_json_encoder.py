import json


class BrainscapesJsonEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__