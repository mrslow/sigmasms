# aiosigmasms

Module provides an interface for https://sigmasms.ru/api/http/.

## Usage

```python
from aiosigmasms import Client

client = Client(username='login', password='password', sender='MessageSender')

# get token
token_resp = await client.login()
token = token_resp['token']

# send message
resp = await client.send_message('+79999999999', 'text', 'sms', token)
print(resp)

# check status
msg_id = resp['id']
status = await client.check_status(msg_id, token)
print(status)

```

## Changelog

| Date         | Changes |
| ------------ | ------- |
| Oct 29, 2019 | - Changed application architecture<br>- Fix tests<br>- Add README.md<br>- Add setup.py |
| Jul 9, 2019  | Release module |
