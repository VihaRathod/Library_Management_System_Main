import pytest
from middleware.rate_limit import RateLimitMiddleware


class FakeClient:
    def __init__(self, host):
        self.host = host


class FakeURL:
    def __init__(self, path):
        self.path = path


class FakeRequest:
    def __init__(self, path="/books", ip="127.0.0.1"):
        self.url = FakeURL(path)
        self.client = FakeClient(ip)


async def fake_call_next(request):
    return "OK"


@pytest.mark.asyncio
async def test_request_allowed_under_limit():

    middleware = RateLimitMiddleware(
        app=None,
        requests_limit=2,
        window_seconds=60
    )

    request = FakeRequest()

    response = await middleware.dispatch(
        request,
        fake_call_next
    )

    assert response == "OK"


@pytest.mark.asyncio
async def test_request_blocked_after_limit():

    middleware = RateLimitMiddleware(
        app=None,
        requests_limit=2,
        window_seconds=60
    )

    request = FakeRequest()

    await middleware.dispatch(request, fake_call_next)
    await middleware.dispatch(request, fake_call_next)

    response = await middleware.dispatch(
        request,
        fake_call_next
    )

    assert response.status_code == 429


@pytest.mark.asyncio
async def test_different_ips_have_separate_limits():

    middleware = RateLimitMiddleware(
        app=None,
        requests_limit=1,
        window_seconds=60
    )

    request_1 = FakeRequest(ip="127.0.0.1")
    request_2 = FakeRequest(ip="192.168.1.10")

    response_1 = await middleware.dispatch(
        request_1,
        fake_call_next
    )

    response_2 = await middleware.dispatch(
        request_2,
        fake_call_next
    )

    assert response_1 == "OK"
    assert response_2 == "OK"