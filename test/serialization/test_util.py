import pytest
import math

from api.serialization.util import instance_to_model

@pytest.mark.parametrize("target, result, error", [
    (None, None, None),
    ("foo", "foo", None),
    (1, 1, None),
    (0.1, 0.1, None),
    (math.nan, None, None),
    ([1, 2], [1, 2], None),
    ((1, 2), [1, 2], None),
    ({"foo": "bar", "one": 2}, {"foo": "bar", "one": 2}, None),
    ({"foo": [1, "bar"]}, {"foo": [1, "bar"]}, None),
    ({"foo": (1, "bar")}, {"foo": [1, "bar"]}, None),
])
def test_instance_to_model(target, result, error):
    if error:
        with pytest.raises(error):
            instance_to_model(target)
            pass
        return
    assert result == instance_to_model(target)
