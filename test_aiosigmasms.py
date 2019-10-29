import pytest
import aiosigmasms

from aioresponses import aioresponses

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def valid_client():
    client = aiosigmasms.Client('user', 'password', 'sender')
    return client


@pytest.fixture
def invalid_client():
    return aiosigmasms.Client(None, None, None)


@pytest.fixture
def token():
    return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'


@pytest.fixture
def mock():
    with aioresponses() as mock:
        yield mock


async def test_login(valid_client, invalid_client, mock, token):
    response = '{"token": "' + token + '", "id": "1", "username": "username"}'
    mock.post('http://online.sigmasms.ru/api/login', status=200, body=response)
    resp = await valid_client.login()
    assert 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' == resp['token']

    with pytest.raises(aiosigmasms.SigmaClientError,
                       match='Username and password are required'):
        await invalid_client.login()


async def test_send_message(valid_client, mock, token):
    response1 = ('{"id": "aca68fa3", "recipient": "+79999999999",'
                 '"status": "pending", "error": null}')
    headers = {'Authorization': token}
    mock.post('http://online.sigmasms.ru/api/sendings', headers=headers,
              body=response1)
    r = await valid_client.send_message('+79999999999', 'test', 'sms', token)
    assert r['error'] is None

    response2 = ('{"id": "aca68fa3", "recipient": "+79999999999",'
                 '"status": "failed", "error": "text"}')
    mock.post('http://online.sigmasms.ru/api/sendings', headers=headers,
              body=response2)
    r = await valid_client.send_message('+79999999999', 'test', 'sms', token)
    assert 'text' == r['error']


async def test_check_status(valid_client, mock, token):
    _id = "aca68fa3"
    response1 = ('{"id": "aca68fa3", "recipient": "+79999999999",'
                 '"state": {"status": "seen", "error": null}}')
    headers = {'Authorization': token}
    mock.get(f'http://online.sigmasms.ru/api/sendings/{_id}', headers=headers,
             body=response1)
    r = await valid_client.check_status(_id, token)
    assert r['state']['error'] is None

    response2 = ('{"id": "aca68fa3", "recipient": "+79999999999",'
                 '"state": {"status": "failed", "error": "text"}}')
    mock.get(f'http://online.sigmasms.ru/api/sendings/{_id}', headers=headers,
             body=response2)
    r = await valid_client.check_status(_id, token)
    assert 'text' == r['state']['error']
