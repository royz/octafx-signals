import config
import requests
from pprint import pprint

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
'AppleWebKit/537.36 (KHTML, like Gecko) '
'Chrome/86.0.4240.198 Safari/537.36'


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
            'user-agent': USER_AGENT,
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

    def update_trades(self, account_number='13102515'):
        headers = {
            'authority': 'www.octafx.com',
            'upgrade-insecure-requests': '1',
            'dnt': '1',
            'user-agent': USER_AGENT,
            'accept': '*/*',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://www.octafx.com/copy-trade/copier-area/',
            'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,sv;q=0.6',
        }

        response = self.session.get(
            f'https://www.octafx.com/copy-trade/change-current-account/copier/{account_number}/copy_trade_copier_area/',
            headers=headers
        )

        with open('trades.html', 'w', encoding='utf-8') as f:
            f.write(response.text)


if __name__ == '__main__':
    login = True
    octafx = Octafx()
    print('logged in:', octafx.login())
    octafx.update_trades(account_number=config.accounts['espada8816'])
