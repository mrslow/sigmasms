import pytest
import aiosigmasms

pytestmark = [pytest.mark.asyncio]

_id = "aca68fa3"
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
headers = {'Authorization': token}
responses = {
    'login': {'token': token, 'id': '1', 'username': 'username'},
    'send_msg_fail': {'id': _id, 'recipient': '+79999999999',
                      'status': 'failed', 'error': 'text'},
    'send_msg_ok': {'id': _id, 'recipient': '+79999999999',
                    'state': 'pending', 'error': None},
    'check_status_ok': {'id': _id, 'recipient': '+79999999999',
                        'state': {'status': 'delivered', 'error': None}},
    'check_status_fail': {'id': _id, 'recipient': '+79999999999',
                          'state': {'status': 'failed', 'error': 'text'}},
}


@pytest.fixture
def valid_client():
    client = aiosigmasms.Client('user', 'password', 'sender')
    return client


@pytest.fixture
def invalid_client():
    return aiosigmasms.Client(None, None, None)


async def test_login_ok(valid_client, httpx_mock):
    httpx_mock.add_response(status_code=200,
                            json=responses['login'],
                            url='http://online.sigmasms.ru/api/login',
                            method='POST')
    resp = await valid_client.login()
    assert token == resp['token']


async def test_login_fail(invalid_client, httpx_mock):
    with pytest.raises(aiosigmasms.SigmaClientError,
                       match='Username and password are required'):
        await invalid_client.login()


async def test_send_message_ok(valid_client, httpx_mock):
    httpx_mock.add_response(status_code=200,
                            url='http://online.sigmasms.ru/api/sendings',
                            headers=headers,
                            json=responses['send_msg_ok'])
    r = await valid_client.send_message('+79999999999', 'test', 'sms', token)
    assert r['error'] is None


async def test_send_message_fail(valid_client, httpx_mock):
    httpx_mock.add_response(status_code=200,
                            url='http://online.sigmasms.ru/api/sendings',
                            headers=headers,
                            json=responses['send_msg_fail'])
    r = await valid_client.send_message('+79999999999', 'test', 'sms', token)
    assert 'text' == r['error']


async def test_check_status_ok(valid_client, httpx_mock):
    httpx_mock.add_response(
        status_code=200,
        url=f'http://online.sigmasms.ru/api/sendings/{_id}',
        headers=headers,
        json=responses['check_status_ok'])
    r = await valid_client.check_status(_id, token)
    assert r['state']['error'] is None


async def test_check_status_fail(valid_client, httpx_mock):
    httpx_mock.add_response(
        status_code=200,
        url=f'http://online.sigmasms.ru/api/sendings/{_id}',
        headers=headers,
        json=responses['check_status_fail'])
    r = await valid_client.check_status(_id, token)
    assert 'text' == r['state']['error']
