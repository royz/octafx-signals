import config
import requests
from pprint import pprint


class Octafx:
    def __init__(self):
        self.session = None

    def login(self):
        self.session = requests.session()
        headers = {
            'authority': 'my.octafx.com',
            'accept': 'application/json, text/plain, */*',
            'dnt': '1',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/86.0.4240.198 Safari/537.36',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://my.octafx.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://my.octafx.com/login/?back=%2Fcopy-trade%2Fcopier-area%2F&fromFront=1',
            'accept-language': 'en-IN,en;q=0.9'
        }

        data = {
            "email": config.email,
            "password": config.password,
            "back": "/copy-trade/copier-area/",
            "fromFront": "1"
        }

        response = self.session.post('https://my.octafx.com/auth/login/', headers=headers, json=data)
        return response.status_code == 200


if __name__ == '__main__':
    octafx = Octafx()
    print(octafx.login())
