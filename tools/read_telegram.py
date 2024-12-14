import requests

TOKEN = ''
API = f'https://api.telegram.org'

request = requests.post(f'{API}/bot{TOKEN}/getUpdates')
print(request.json())