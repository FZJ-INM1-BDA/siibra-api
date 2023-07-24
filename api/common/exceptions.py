class SapiBaseException(Exception): pass

class InsufficientParameters(SapiBaseException):
    """InsufficientParameters"""

class AmbiguousParameters(SapiBaseException):
    """AmbiguousParameters"""

class NotFound(SapiBaseException):
    """NotFound"""

class InvalidParameters(SapiBaseException):
    """InvalidParameters"""

class SerializationException(SapiBaseException):
    """SerializationException"""

class ClsNotRegisteredException(SerializationException):
    """ClsNotRegisteredException"""

class NonStrKeyException(SerializationException):
    """NonStrKeyException"""

class ConfigException(SapiBaseException):
    """ConfigException"""

class FaultyRoleException(ConfigException):
    """FaultyRoleException"""