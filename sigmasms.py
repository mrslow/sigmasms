import httpx

from typing import Optional

__all__ = ['Client', 'AsyncClient', 'SigmaClientError']

_BASE_URL = 'http://online.sigmasms.ru/api'


class SigmaClientError(Exception):
    pass


class BaseClient:

    def __init__(self, username: str, password: str, sender: Optional[str]):
        self.username: str = username
        self.password: str = password
        self.sender: str = sender
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None

    def prepare_payload(self, rcpt, msg, msg_type):
        return {
            'recipient': rcpt,
            'type': msg_type,
            'payload': {
                'sender': self.sender,
                'text': msg
            }
        }


class Client(BaseClient):

    def __init__(self, username: str, password: str, sender: Optional[str]):
        super().__init__(username, password, sender)
        self.client: httpx.Client = httpx.Client(base_url=_BASE_URL, timeout=60)

    def close(self):
        self.client.close()

    def _request(self, method, path, **kwargs):
        if self.token is not None:
            kwargs['headers'] = {'Authorization': self.token}
        resp = self.client.request(method, path, **kwargs)
        return resp.json()

    def auth(self):
        if not (self.username or self.password):
            raise SigmaClientError('Username and password are required')
        data = {'username': self.username, 'password': self.password}
        resp = self._request('POST', 'login',  json=data)
        self.user_id = resp['id']
        self.token = resp['token']

    def send_message(self, rcpt, msg, msg_type):
        payload = self.prepare_payload(rcpt, msg, msg_type)
        return self._request('POST', 'sendings', json=payload)

    def check_status(self, message_id):
        return self._request('GET', f'sendings/{message_id}')

    def get_balance(self):
        resp = self._request('GET', f'users/{self.user_id}')
        return resp['balance']


class AsyncClient(BaseClient):

    def __init__(self, username: str, password: str, sender: Optional[str]):
        super().__init__(username, password, sender)
        self.client: httpx.AsyncClient = httpx.AsyncClient(base_url=_BASE_URL,
                                                           timeout=60)

    async def close(self):
        await self.client.aclose()

    async def _request(self, method, path, **kwargs):
        if self.token is not None:
            kwargs['headers'] = {'Authorization': self.token}
        resp = await self.client.request(method, path, **kwargs)
        return resp.json()

    async def auth(self):
        if not (self.username or self.password):
            raise SigmaClientError('Username and password are required')
        data = {'username': self.username, 'password': self.password}
        resp = await self._request('POST', 'login',  json=data)
        self.user_id = resp['id']
        self.token = resp['token']

    async def send_message(self, rcpt, msg, msg_type):
        payload = self.prepare_payload(rcpt, msg, msg_type)
        return await self._request('POST', 'sendings', json=payload)

    async def check_status(self, message_id):
        return await self._request('GET', f'sendings/{message_id}')

    async def get_balance(self):
        resp = await self._request('GET', f'users/{self.user_id}')
        return resp['balance']