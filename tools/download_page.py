import requests

URL = ''

with open('./index.html', 'w') as f:
    f.write(requests.get(URL).text)
