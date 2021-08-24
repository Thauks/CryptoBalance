import yaml
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from coinbase.wallet.client import Client as CoinbaseClient
from binance.client import Client as BinanceClient

with open('../config/config.yml') as cnf:
    config = yaml.load(cnf, Loader=yaml.FullLoader)

print(config)

CbClient = CoinbaseClient(api_key=config['CB_API_KEY'], api_secret=config['CB_API_SECRET'])
BnClient = BinanceClient(api_key=config['BN_API_KEY'], api_secret=config['CB_API_SECRET'])


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

    return wallet_last, wallet_avg

updater = Updater(config['BOT_API_KEY'])

dispatcher = updater.dispatcher

# updater.dispatcher.add_handler(CommandHandler('hello', get_balance(CbClient, BnClient, updater)))



updater.start_polling()
updater.idle()