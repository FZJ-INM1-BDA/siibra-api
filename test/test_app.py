import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from unittest.mock import MagicMock, patch
from starlette.requests import Request

from starlette.responses import StreamingResponse
from app.app import app, cache_response, __version__
from app.configuration.cache_redis import CacheRedis

client = TestClient(app)


# Test template returns
# TemplateNotFound Error

@pytest.mark.asyncio
async def test_home():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    # response = client.get("/")
    assert response.status_code == 200
    assert 'Siibra' in str(response.content)


@pytest.mark.asyncio
async def test_stats():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/stats")
    assert response.status_code == 200
    assert 'Siibra - statistics' in str(response.content)


class MockRedis:
    def get_value(self, key):
        pass
    def set_value(self, key, value):
        pass


mock_redis = MockRedis()

class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


def get_request_obj(hdr=[]):
    return Request(scope={
        "type": "http",
        "method": "get",
        "path": "/",
        "headers": hdr
    })

def generate_json(input: dict) -> bytes:
    import json
    yield bytes(json.dumps(input), "utf-8")

@pytest.mark.asyncio
async def test_cache_response_get_instance_called():
    with patch.object(CacheRedis, 'get_instance', return_value=mock_redis) as patched_get_instance:
        request = get_request_obj(hdr=[
            (b"accept", b"text/html")
        ])
        call_next = AsyncMock()

        call_next.return_value = StreamingResponse(
            generate_json({"foo": "bar"}),
            media_type="application/json"
        )
        await cache_response(request, call_next)
        patched_get_instance.assert_called()

test_header_params = ("hdr,called", [
    ([], True),
    ([(b"x-bypass-fast-api-cache", b"true")], False)
])

@pytest.mark.parametrize(*test_header_params)
@pytest.mark.asyncio
async def test_cache_response_bypass_header(hdr,called):
    with patch.object(CacheRedis, 'get_instance', return_value=mock_redis):
        with patch.object(mock_redis, 'get_value') as get_value_mock:
            request= get_request_obj(hdr=hdr)
            call_next = AsyncMock()
            call_next.return_value = StreamingResponse(
                generate_json({"foo": "bar"}),
                media_type="application/json"
            )
            await cache_response(request, call_next)
            if called:
                get_value_mock.assert_called_once()
            else:
                get_value_mock.assert_not_called()

test_cache_hit_params = ("get_value_returns,expect_cache_hit_header,expect_call_next_called", [
    ('{"foo": "bar"}', True, False),
    (None, False, True)
])

@pytest.mark.parametrize(*test_cache_hit_params)
@pytest.mark.asyncio
async def test_cache_response_hit_cache(get_value_returns,expect_cache_hit_header,expect_call_next_called):
    with patch.object(CacheRedis, 'get_instance', return_value=mock_redis):
        with patch.object(mock_redis, 'get_value', return_value=get_value_returns):
            request= get_request_obj(hdr=[])
            call_next = AsyncMock()
            call_next.return_value = StreamingResponse(
                generate_json({"hello": "world"}),
                media_type="application/json"
            )
            resp = await cache_response(request, call_next)
            
            if expect_call_next_called:
                call_next.assert_called_once()
            else:
                call_next.assert_not_called()
            
            if expect_cache_hit_header:
                assert resp.headers.get("x-fastapi-cache") is not None
            else:
                assert resp.headers.get("x-fastapi-cache") is None

            if get_value_returns:
                assert resp.body.decode("utf-8") == get_value_returns
            else:
                assert resp.body.decode("utf-8") == '{"hello": "world"}'

test_cache_miss_params = ("call_next_raises_flag,call_next_status,call_next_returns,media_type,set_value_called", [
    (True,None,None,None,False),
    (False,200,{"fooz": "barz"},"application/json",True),
    (False,404,{"fooz": "barz"},"application/json",False),
    (False,200,{"hello": "world"}, "text/plain", False),
])

@pytest.mark.parametrize(*test_cache_miss_params)
@pytest.mark.asyncio
async def test_cache_response_miss(call_next_raises_flag,call_next_status,call_next_returns,media_type,set_value_called):
    with patch.object(CacheRedis, 'get_instance', return_value=mock_redis):
        with patch.object(mock_redis, 'get_value', return_value=None):
            with patch.object(mock_redis, 'set_value') as set_value_handle:
                request= get_request_obj(hdr=[])

                class TmpException(Exception): pass
                call_next = AsyncMock()

                if call_next_raises_flag:
                    call_next.side_effect = TmpException("bla")
                else:
                    call_next.return_value = StreamingResponse(
                        generate_json(call_next_returns),
                        media_type=media_type,
                        status_code=call_next_status
                    )
                try:
                    await cache_response(request, call_next)
                    assert not call_next_raises_flag
                except TmpException:
                    assert call_next_raises_flag, f"if call_next_raises_flag is True, expect exception to be raised"
                
                if set_value_called:
                    import json
                    set_value_handle.assert_called_once_with(f"[{__version__}] /", bytes(json.dumps(call_next_returns), "utf-8"))
                else:
                    set_value_handle.assert_not_called()
