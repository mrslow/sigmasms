import pytest
import aiosigmasms

from aioresponses import aioresponses

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def valid_client():
    client = aiosigmasms.Client()
    client.username = 'user'
    client.password = 'pass'
    client.sender = 'sender'
    return client


@pytest.fixture
def invalid_client():
    return aiosigmasms.Client()


@pytest.fixture
def mock():
    with aioresponses() as mock:
        yield mock


async def test_auth(valid_client, invalid_client, mock):
    response = ('{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", "id": "1",'
                '"username": "username"}')
    mock.post('http://online.sigmasms.ru/api/login', status=200, body=response)
    await valid_client.auth()
    assert 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' == valid_client.token

    with pytest.raises(ValueError):
        await invalid_client.auth()


async def test_send_message(valid_client, mock):
    valid_client.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
    response1 = ('{"id": "aca68fa3", "recipient": "+79999999999",'
                 '"status": "pending", "error": null}')
    headers = {'Authorization': valid_client.token}
    mock.post('http://online.sigmasms.ru/api/sendings', headers=headers,
              body=response1)
    r = await valid_client.send_message('+79999999999', 'test', 'sms')
    assert r['error'] is None

    response2 = ('{"id": "aca68fa3", "recipient": "+79999999999",'
                 '"status": "failed", "error": "text"}')
    mock.post('http://online.sigmasms.ru/api/sendings', headers=headers,
              body=response2)
    r = await valid_client.send_message('+79999999999', 'test', 'sms')
    assert 'text' == r['error']


async def test_check_status(valid_client, mock):
    valid_client.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
    _id = "aca68fa3"
    response1 = ('{"id": "aca68fa3", "recipient": "+79999999999",'
                 '"state": {"status": "seen", "error": null}}')
    headers = {'Authorization': valid_client.token}
    mock.get(f'http://online.sigmasms.ru/api/sendings/{_id}', headers=headers,
             body=response1)
    r = await valid_client.check_status(_id)
    assert r['state']['error'] is None

    response2 = ('{"id": "aca68fa3", "recipient": "+79999999999",'
                 '"state": {"status": "failed", "error": "text"}}')
    mock.get(f'http://online.sigmasms.ru/api/sendings/{_id}', headers=headers,
             body=response2)
    r = await valid_client.check_status(_id)
    assert 'text' == r['state']['error']
