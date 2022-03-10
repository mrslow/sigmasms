import pytest
import pytest_asyncio

from sigmasms import Client, AsyncClient, SigmaClientError

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
    'balance': {'Tariffs': [],  'balance': 100, 'isActive': True}
}


@pytest.fixture
def valid_sync_client():
    client = Client('user', 'password', 'sender')
    client.token = token
    client.user_id = '1'
    yield client
    client.close()


@pytest_asyncio.fixture
async def valid_async_client():
    client = AsyncClient('user', 'password', 'sender')
    client.token = token
    client.user_id = '1'
    yield client
    await client.close()


@pytest.mark.asyncio
async def test_auth_ok(httpx_mock):
    httpx_mock.add_response(status_code=200,
                            json=responses['login'],
                            url='http://online.sigmasms.ru/api/login',
                            method='POST')
    client = AsyncClient('user', 'password', 'sender')
    await client.auth()
    assert client.token == token
    assert client.user_id == '1'


@pytest.mark.asyncio
async def test_auth_fail(httpx_mock):
    with pytest.raises(SigmaClientError,
                       match='Username and password are required'):
        client = AsyncClient('', '', 'sender')
        await client.auth()


@pytest.mark.asyncio
async def test_send_message_ok(valid_async_client, httpx_mock):
    httpx_mock.add_response(status_code=200,
                            url='http://online.sigmasms.ru/api/sendings',
                            headers=headers,
                            json=responses['send_msg_ok'])
    r = await valid_async_client.send_message('+79999999999', 'test', 'sms')
    assert r['error'] is None


@pytest.mark.asyncio
async def test_send_message_fail(valid_async_client, httpx_mock):
    httpx_mock.add_response(status_code=200,
                            url='http://online.sigmasms.ru/api/sendings',
                            headers=headers,
                            json=responses['send_msg_fail'])
    r = await valid_async_client.send_message('+79999999999', 'test', 'sms')
    assert 'text' == r['error']


@pytest.mark.asyncio
async def test_check_status_ok(valid_async_client, httpx_mock):
    httpx_mock.add_response(
        status_code=200,
        url=f'http://online.sigmasms.ru/api/sendings/{_id}',
        headers=headers,
        json=responses['check_status_ok'])
    r = await valid_async_client.check_status(_id)
    assert r['state']['error'] is None


@pytest.mark.asyncio
async def test_check_status_fail(valid_async_client, httpx_mock):
    httpx_mock.add_response(
        status_code=200,
        url=f'http://online.sigmasms.ru/api/sendings/{_id}',
        headers=headers,
        json=responses['check_status_fail'])
    r = await valid_async_client.check_status(_id)
    assert 'text' == r['state']['error']


@pytest.mark.asyncio
async def test_get_balance(valid_async_client, httpx_mock):
    httpx_mock.add_response(
        status_code=200,
        url=f'http://online.sigmasms.ru/api/users/{responses["login"]["id"]}',
        headers=headers,
        json=responses['balance'])
    balance = await valid_async_client.get_balance()
    assert balance == 100


def test_sync_auth_ok(httpx_mock):
    httpx_mock.add_response(status_code=200,
                            json=responses['login'],
                            url='http://online.sigmasms.ru/api/login',
                            method='POST')
    client = Client('user', 'password', 'sender')
    client.auth()
    assert client.token == token
    assert client.user_id == '1'


def test_sync_auth_fail(httpx_mock):
    with pytest.raises(SigmaClientError,
                       match='Username and password are required'):
        client = Client('', '', 'sender')
        client.auth()


def test_sync_send_message_ok(valid_sync_client, httpx_mock):
    httpx_mock.add_response(status_code=200,
                            url='http://online.sigmasms.ru/api/sendings',
                            headers=headers,
                            json=responses['send_msg_ok'])
    r = valid_sync_client.send_message('+79999999999', 'test', 'sms')
    assert r['error'] is None


def test_sync_send_message_fail(valid_sync_client, httpx_mock):
    httpx_mock.add_response(status_code=200,
                            url='http://online.sigmasms.ru/api/sendings',
                            headers=headers,
                            json=responses['send_msg_fail'])
    r = valid_sync_client.send_message('+79999999999', 'test', 'sms')
    assert 'text' == r['error']


def test_sync_check_status_ok(valid_sync_client, httpx_mock):
    httpx_mock.add_response(
        status_code=200,
        url=f'http://online.sigmasms.ru/api/sendings/{_id}',
        headers=headers,
        json=responses['check_status_ok'])
    r = valid_sync_client.check_status(_id)
    assert r['state']['error'] is None


def test_sync_check_status_fail(valid_sync_client, httpx_mock):
    httpx_mock.add_response(
        status_code=200,
        url=f'http://online.sigmasms.ru/api/sendings/{_id}',
        headers=headers,
        json=responses['check_status_fail'])
    r = valid_sync_client.check_status(_id)
    assert 'text' == r['state']['error']


def test_sync_get_balance(valid_sync_client, httpx_mock):
    httpx_mock.add_response(
        status_code=200,
        url=f'http://online.sigmasms.ru/api/users/{responses["login"]["id"]}',
        headers=headers,
        json=responses['balance'])
    balance = valid_sync_client.get_balance()
    assert balance == 100
