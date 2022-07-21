import unittest
from app.configuration.siibra_custom_exception import SiibraCustomException


class TestTokenWrapper(unittest.TestCase):

    def test_default_exception_status(self):
        custom_exception = SiibraCustomException('Some error')
        self.assertEqual(custom_exception.status_code, 500)

    def test_message_is_set(self):
        msg = 'My message'
        custom_exception = SiibraCustomException(msg)
        self.assertEqual(custom_exception.message, msg)

    def test_status_code_is_set(self):
        msg = 'My message'
        status = 418
        custom_exception = SiibraCustomException(msg, status_code=status)
        self.assertEqual(custom_exception.status_code, status)
