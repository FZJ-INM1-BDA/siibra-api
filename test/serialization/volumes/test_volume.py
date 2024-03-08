from unittest.mock import patch
import pytest

from api.serialization.volumes.volume import remap_provider
from api import siibra_api_config

@pytest.fixture
def provider():
    siibra_api_config.SIIBRA_API_REMAP_PROVIDERS["http://foo.bar"] = "http://bazz.bizz"
    siibra_api_config.SIIBRA_API_REMAP_PROVIDERS["http://hello.world"] = "http://apple.banana"
    yield {
        "foo": "http://foo.bar/two/one",
        "bar": "http://hello.world/me/you",
        "bazz": "http://bazz.bizz/cable/two"
    }
    siibra_api_config.SIIBRA_API_REMAP_PROVIDERS.clear()

def test_remap_provider(provider):
    remap_provider(provider)
    assert provider["foo"] == "http://bazz.bizz/two/one"
    assert provider["bar"] == "http://apple.banana/me/you"
    assert provider["bazz"] == "http://bazz.bizz/cable/two"
