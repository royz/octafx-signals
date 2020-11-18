import os
import sys
import time
import random
import config
import logging
import requests
from pprint import pprint
from bs4 import BeautifulSoup

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

        response = self.session.post('https://my.octafx.com/auth/login/',
                                     headers=headers, json=data)
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

        try:
            response = self.session.get(f'https://www.octafx.com/copy-trade/change-current-account/copier/'
                                        f'{account_number}/copy_trade_copier_area/', headers=headers)
        except Exception as e:
            logger.error(err(e))
            random_sleep()
            logger.info('retrying...')
            return self.update_trades(account_number)

        # if status code is not 200 that might mean we need to log in again
        if response.status_code != 200:
            logger.warning(f'status code: {response.status_code}. logging in again...')
            random_sleep()
            self.login()
            return self.update_trades(account_number)

        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table', {'class': 'ct-stats-table'})
        if len(tables) >= 2:
            closed_trades_table = tables[0]
            open_trades_table = tables[1]
        else:
            return None

        trades = []

        try:
            # get all closed trades
            closed_trades = closed_trades_table.find('tbody').find_all('tr')
            for trade in closed_trades:
                try:
                    cols = trade.find_all('td')
                    _symbol = cols[2].text.strip()
                    _type = cols[1].text.strip()
                    _id = trade['data-deal-id']
                    if _type == 'Bonus':
                        continue
                    trades.append({
                        'id': _id,
                        'symbol': _symbol,
                        'type': _type,
                        'group': 'closed'
                    })
                except Exception as e:
                    logger.error(err(e))

            # get all open trades
            open_trades = open_trades_table.find('tbody').find_all('tr')
            for trade in open_trades:
                try:
                    cols = trade.find_all('td')
                    _symbol = cols[2].text.strip()
                    _type = cols[1].text.strip()
                    _id = trade['data-deal-id']

                    trades.append({
                        'id': _id,
                        'symbol': _symbol,
                        'type': _type,
                        'group': 'open'
                    })
                except Exception as e:
                    logger.error(err(e))
        except Exception as e:
            logger.error(err(e))
            random_sleep()
            return self.update_trades(account_number)
        return trades


def err(e):
    return ' '.join(str(e).split())


def random_sleep():
    time.sleep(random.randint(7, 16))


class Telegram:
    def send_notification(self):
        pass


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        handlers=(
            logging.FileHandler(filename=os.path.join(os.path.dirname(__file__), 'octafx.log')),
            logging.StreamHandler(sys.stdout)
        )
    )
    logging.getLogger(requests.__name__).setLevel(logging.ERROR)
    logger = logging.getLogger()

    octafx = Octafx()
    print('logged in:', octafx.login())
    octafx.update_trades(account_number=config.accounts['Sparrow13']['id'])
