import requests
import json
import time
from datetime import datetime
import logging
import telebot
from ordermanager import Order
from dbmanager import DBManager

file_loc =""
with open(file_loc+'config.json') as config_file:
    config = json.load(config_file)

name = config['name']
symbol = config['symbol']

bot = telebot.TeleBot(config["token"], parse_mode=None)

db = DBManager("file_loc+data/elrondStats.db")


def log_message(message, level):
    now = time.time()
    at = time.strftime("%Y-%m-%d %H: %M", time.localtime(now))

    if level == "command":
        print(f"{level} | ({at}): Received command: {message.text}. From: {message.chat.id}. User: {message.from_user.username}. Name: {message.from_user.first_name} {message.from_user.last_name}")
        logging.info(
            f"Received command: {message.text}. From: {message.chat.id}. User: {message.from_user.username}. Name: {message.from_user.first_name} {message.from_user.last_name}")
    elif level == 'info':
        print(f"{level} | ({at}): {message}")
        logging.info(message)
    elif level == "debug":
        print(f"{level} | ({at}): {message}")
        logging.info(message)
    elif level == "error":
        print(f"{level} | ({at}): {message}")
        logging.error(message)



def main():
    orders = []
    while True:
        try:
            payload = config['binance_price']
            price_usd = requests.get(config["binance_url"] + "ticker/price", params=payload)
            if(price_usd.status_code==200):
                # log_message("Fetched price.", "info")
                price_usd_data = float(price_usd.json()['price'])
                min_quote=config["min_quote"]/price_usd_data

                payload = config['binance_ticker']
                trades = requests.get(config["binance_url"]+"trades", params=payload)
                if(trades.status_code ==200):
                    # log_message("Fetched trades data.", "info")
                    trades_data = trades.json()

                    large_orders = list(filter(lambda x: float(x['quoteQty'])>=min_quote,trades_data))

                    if(len(large_orders)>0):
                        log_message("Large order confirmed.","info")
                        ids = list(map(lambda x: x.id, orders))
                        subscribed_ids = db.get_ids()
                        for large_order in large_orders:
                            if(str(large_order['id']) not in ids):
                                quote_qty = "{:,.8f}".format(float(large_order['quoteQty']))
                                price_usd = "{:,.0f}".format(price_usd_data * float(large_order['quoteQty']))
                                price_usd_raw = price_usd_data * float(large_order['quoteQty'])
                                base_qty = "{:,.0f}".format(float(large_order['qty']))
                                price_btc = "{:,.8f}".format(float(large_order['price']))
                                is_seller = large_order['isBuyerMaker']
                                order_type = "🧯[SELL]🧯" if is_seller else "🔥[BUY]🔥"
                                ts = float(large_order['time'])/1000
                                at = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                                log_message(str(large_order['id'])+ " added to memory","info")
                                orders.append(Order(large_order['id'], config['max_life_m']))
                                for id in subscribed_ids:
                                    if id[1] < price_usd_raw: 
                                        bot.send_message(id[0], f"*Large {order_type} Order*:\n\nValuation *[USD]*: *${price_usd}*\nValuation *[BTC]*: *{quote_qty}₿*\nAmount *[{symbol}]*: *{base_qty}*\nPrice *[BTC]*:*{price_btc}*\n\n(At: {at})", parse_mode="Markdown")
                                        log_message(f"Sent message to: {id[0]}", "info")
                else:
                    log_message("Failed with status code: "+ price_usd.status_code, "error")
            else:
                log_message("Failed with status code: "+ price_usd.status_code, "error")


            dead = list(filter(lambda x: x.checkLife()==False, orders))
            orders = list(filter(lambda x: x.checkLife(), orders))
            if len(dead)>0:
                log_message(f"Removed id: {dead}","info")
            time.sleep(config['binance_interval_m']*60)
        except Exception as e:
            log_message(e,"error")
            time.sleep(config['binance_interval_m']*60)


if __name__ == "__main__":
    now = time.time()
    logging.basicConfig(filename=file_loc+f'log/binanceapi/{now}.log',
                        level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    main()