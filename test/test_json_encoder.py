"""
Tests for default json encoder
"""
import unittest
from app.brainscapes_json_encoder import BrainscapesJsonEncoder


class DummyObject:
    def __init__(self):
        self.id = 1
        self.name = 'dummy'


class TestJsonEncoder(unittest.TestCase):

    def test_object_encoder(self):
        data = DummyObject()
        data_as_string = BrainscapesJsonEncoder().encode(o=data)
        self.assertTrue(
            '{"id": 1, "name": "dummy"}' in data_as_string
        )


if __name__ == '__main__':
    unittest.main()
