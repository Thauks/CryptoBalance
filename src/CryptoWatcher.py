import os
import time

import yaml
from telegram.ext import Updater, CommandHandler, CallbackContext, run_async
from coinbase.wallet.client import Client as CoinbaseClient
from binance.client import Client as BinanceClient
from boto.s3.connection import S3Connection

# Declaring config and the necessary clients to make the requests

print(os.environ['CB_API_KEY'])
try:
    with open('../config/config.yml') as cnf:
        config = yaml.load(cnf, Loader=yaml.FullLoader)

    CbClient = CoinbaseClient(api_key=config['CB_API_KEY'], api_secret=config['CB_API_SECRET'])
    BnClient = BinanceClient(api_key=config['BN_API_KEY'], api_secret=config['CB_API_SECRET'])
    updater = Updater(config['BOT_API_KEY'])

except:
    CbClient = CoinbaseClient(api_key=os.environ['CB_API_KEY'], api_secret=os.environ['CB_API_SECRET'])
    BnClient = BinanceClient(api_key=os.environ['BN_API_KEY'], api_secret=os.environ['CB_API_SECRET'])
    updater = Updater(os.environ['BOT_API_KEY'])


# Declaring the functions needed by the logic

def get_balance(CbClient, BnClient):
    accounts = CbClient.get_accounts(limit=100)['data']
    tickers = BnClient.get_all_tickers()

    wallet_avg = 0
    wallet_last = 0

    for account in accounts:
        obj = account['balance']
        amount = obj['amount']
        curr = obj['currency']
        ticker = curr + 'EUR'
        if float(amount) > 0.01:
            avg_price = BnClient.get_avg_price(symbol=ticker)['price']
            last_price = 0
            for tk in tickers:
                if tk['symbol'] == ticker:
                    last_price = tk['price']
            print(curr, amount, last_price, avg_price)
            wallet_last += float(amount) * float(last_price)
            wallet_avg += float(amount) * float(avg_price)

    return round(wallet_last, ndigits=2), round(wallet_avg, ndigits=2)


def telegram_handler(update, context):
    while True:
        last, avg = get_balance(CbClient, BnClient)
        update.message.reply_text(f'Current Balance: {last}')
        print(context.args)
        seconds = 1800
        try:
            seconds = int(context.args[0])
        except:
            pass
        time.sleep(seconds)


def stopper(update, context):
    update.message.reply_text(f'Stopped.')
    os._exit(0)


# Running the bot

updater.dispatcher.add_handler(CommandHandler('start', telegram_handler, run_async=True))
updater.dispatcher.add_handler(CommandHandler('stop', stopper, run_async=True))

updater.start_polling()
updater.idle()
