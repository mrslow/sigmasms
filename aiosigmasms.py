import aiohttp
import logging

__all__ = ['Client']


class Client:

    BASE_URL = 'http://online.sigmasms.ru/api'

    def __init__(self, username=None, password=None, sender=None):
        self.username = username
        self.password = password
        self.sender = sender
        self.token = None

    async def auth(self):
        if not (self.username and self.password):
            raise ValueError('Login and password are required')
        if not self.token:
            await self._set_token()

    async def _set_token(self):
        url = f'{self.BASE_URL}/login'
        data = {'username': self.username, 'password': self.password}
        async with aiohttp.ClientSession() as client:
            async with client.post(url, json=data) as resp:
                json = await resp.json()
                self.token = json['token'] if not json.get('error') else None

    async def _request(self, method, url, **kwargs):
        await self.auth()
        if self.token:
            async with aiohttp.ClientSession() as client:
                async with client.request(method, url, **kwargs) as resp:
                    return await resp.json()

    async def send_message(self, recipient, message, type):
        url = f'{self.BASE_URL}/sendings'
        payload = {
            'recipient': recipient,
            'type': type,
            'payload': {
                'sender': self.sender,
                'text': message
            }
        }
        headers = {'Authorization': self.token}
        resp = await self._request('POST', url, json=payload, headers=headers)
        return resp

    async def check_status(self, message_id):
        url = f'{self.BASE_URL}/sendings/{message_id}'
        headers = {'Authorization': self.token}
        resp = await self._request('GET', url, headers=headers)
        return resp
