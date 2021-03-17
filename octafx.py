import os
import sys
import time
import random
import config
import logging
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' + \
             'AppleWebKit/537.36 (KHTML, like Gecko) ' + \
             'Chrome/86.0.4240.198 Safari/537.36'


class Octafx:
    def __init__(self):
        self.cookies = None

    def login(self):
        with webdriver.Firefox() as driver:
            # visit the login page
            driver.get('https://my.octafx.com/auth/login/')

            try:
                element_present = ec.presence_of_element_located((By.CSS_SELECTOR, 'input[name="email"]'))
                WebDriverWait(driver, 15).until(element_present)

                # enter email and password
                driver.find_element_by_css_selector('input[name="email"]').send_keys(config.email)
                driver.find_element_by_css_selector('input[name="password"]').send_keys(config.password)

                # get the current url before logging in
                current_url = driver.current_url

                # check if captcha was shown
                try:
                    if driver.find_element_by_id('captchaContainerId_1'):
                        print('solve the captcha and click login')
                    else:
                        driver.find_element_by_css_selector(
                            'button[data-auto-event-action="Sign In form click"]').click()
                except:
                    # login
                    driver.find_element_by_css_selector('button[data-auto-event-action="Sign In form click"]').click()

                # wait for next page to load
                while driver.current_url == current_url:
                    time.sleep(1)

                # then wait for 5 seconds
                time.sleep(5)

                # get the cookies
                self.cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
                return True
            except TimeoutException:
                print("Timed out waiting for page to load")
                return False

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
            response = requests.get(f'https://www.octafx.com/copy-trade/change-current-account/copier/'
                                    f'{account_number}/copy_trade_copier_area/', headers=headers, cookies=self.cookies)
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
                    if _type == 'Bonus' or _type == 'Deposit':
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


def send_notification(account, trade_info):
    telegram_account = account['telegram']
    logger.info(
        f'new notification for {account["user"]}: {trade_info["group"]} | {trade_info["symbol"]} | {trade_info["type"]}'
    )

    url = f'https://api.telegram.org/bot{telegram_account["token"]}/sendMessage'

    if trade_info["group"] == "open":
        text = f'Order {trade_info["id"]}\n' \
               f'===[ NEW ]===========' \
               f' {trade_info["symbol"]} {trade_info["type"]}\n' \
               f'==================='
    else:
        text = f'Close signal\n' \
               f'Order {trade_info["id"]}\n' \
               f'===CLOSED===========\n' \
               f' {trade_info["symbol"]} CLOSE\n' \
               f'==================='

    params = {
        'chat_id': telegram_account['chat_id'],
        'text': text
    }

    try:
        resp = requests.get(url, params=params)
        if resp.json()['ok']:
            logger.info('notification sent successfully')
        else:
            logger.warning('could not send notification')
    except Exception as e:
        logger.error(err(e))


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        handlers=(
            logging.FileHandler(filename=os.path.join(os.path.dirname(__file__), 'octafx.log')),
            logging.StreamHandler(sys.stdout)
        )
    )
    logging.getLogger('requests').setLevel(logging.ERROR)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logger = logging.getLogger()

    octafx = Octafx()
    logger.info('logging in...')

    if octafx.login():
        logger.info('logged in')
    else:
        logger.error('failed to log in')
        quit()

    unique_trade_ids = []  # a list of unique ids of all previous trades

    first_iter = True
    while True:
        for account in config.accounts:
            trades = octafx.update_trades(account_number=account['id'])
            if trades is None:
                continue

            new_trades = []
            for trade in trades:
                unique_trade_id = f'{trade["group"]}-{trade["id"]}'
                if unique_trade_id in unique_trade_ids:
                    continue
                else:
                    unique_trade_ids.append(unique_trade_id)
                    if not first_iter:
                        # do not send notifications on first check
                        new_trades.append(trade)

            logger.info(f'{len(trades)} trades found for {account["user"]}. {len(new_trades)} new.')

            for trade in new_trades:
                send_notification(account, trade)

            random_sleep()
        first_iter = False
