import httpx

__all__ = ['Client', 'SigmaClientError']


class SigmaClientError(Exception):
    pass


class Client:

    _BASE_URL = 'http://online.sigmasms.ru/api'

    def __init__(self, username, password, sender):
        self.username = username
        self.password = password
        self.sender = sender

    async def _request(self, method, endpoint, **kwargs):
        async with httpx.AsyncClient(base_url=self._BASE_URL) as client:
            resp = await client.request(method, endpoint, **kwargs)
            return resp.json()

    async def login(self):
        if not (self.username or self.password):
            raise SigmaClientError('Username and password are required')
        data = {'username': self.username, 'password': self.password}
        resp = await self._request('POST', 'login',  json=data)
        return resp

    async def send_message(self, rcpt, msg, msg_type, token):
        payload = {
            'recipient': rcpt,
            'type': msg_type,
            'payload': {
                'sender': self.sender,
                'text': msg
            }
        }
        headers = {'Authorization': token}
        resp = await self._request('POST', 'sendings', json=payload,
                                   headers=headers)
        return resp

    async def check_status(self, message_id, token):
        headers = {'Authorization': token}
        endpoint = f'sendings/{message_id}'
        resp = await self._request('GET', endpoint, headers=headers)
        return resp
