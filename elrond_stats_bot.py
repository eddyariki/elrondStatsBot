import json
import telebot
import logging
import time
import requests
from signal import signal, SIGINT
from dbmanager import DBManager

print("Starting...")

"""
--------------------------------------------------------------------------
Setup
--------------------------------------------------------------------------
"""

with open('config.json') as config_file:
    config = json.load(config_file)

bot = telebot.TeleBot(config["token"], parse_mode=None)
coin = config['coin']
name = config['name']
symbol = config['symbol']
db = DBManager("data/elrondStats.db")


"""
--------------------------------------------------------------------------
Bot Message Handlers
--------------------------------------------------------------------------
"""

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    log_message(message, "command")
    bot.send_message(message.chat.id, config["welcome"])

@bot.message_handler(commands=['subscribe', 'unsubscribe'])
def command_sub(message):
    log_message(message, "command")
    if(message.text=="/subscribe"):
        db.insert(message.chat.id)
        db.backup("backup")
        bot.send_message(message.chat.id, "Subscribed to Elrond Stats Bot")
    elif(message.text=="/unsubscribe"):
        db.delete(message.chat.id)
        db.backup("backup")
        bot.send_message(message.chat.id, "Unsubscribed to Elrond Stats Bot")

@bot.message_handler(commands=['p', 'price'])
def command_price(message):
    log_message(message, "command")
    try:
        payload = config['price_config']
        r = requests.get(config["url"]+"simple/price", params=payload)
        if(r.status_code == 200):
            log_message("Fetched price successfully.", 'info')
            data = r.json()['elrond']
            price_usd = "{:,}".format(data["usd"])
            price_btc = "{:,.8f}".format(data["btc"])
            price_eth = "{:,.8f}".format(data["eth"])
            market_cap = "{:,.0f}".format(data['usd_market_cap'])
            volume = "{:,.0f}".format(data['usd_24h_vol'])
            bot.send_message(
                message.chat.id, f"Price of {name} *[{symbol}]*\n\n*[USD]*: ${price_usd}\n*[BTC]*: {price_btc}₿\n*[ETH]*: {price_eth}Ξ\n📊Volume: ${volume}\nⓂ️Market Cap: ${market_cap}", parse_mode='Markdown')
        else:
            log_message(f"Get request failed with :{r.status_code}", "error")
            bot.send_message(config['debug_chat_id'], f"Get request failed with :{r.status_code}")

    except Exception as e:
        log_message(e, 'error')
        bot.send_message(config['debug_chat_id'], f"Get request failed with :{e}")
        time.sleep(5)

@bot.message_handler(commands=['change','c'])
def command_change(message):
    log_message(message, "command")
    try:
        payload = config['market_config']
        r = requests.get(config["url"]+f"coins/{coin}", params=payload)
        if(r.status_code == 200):
            log_message("Fetched market data successfully.", 'info')
            data=r.json()
            mData=data['market_data']
            c24h=round(mData["price_change_percentage_24h"],1)
            c7d=round(mData["price_change_percentage_7d"],1)
            c30d=round(mData["price_change_percentage_30d"],1)
            c200d=round(mData["price_change_percentage_200d"],1)
            c1y=round(mData["price_change_percentage_1y"],1)
            marketcap_change_24h = "{:,.0f}".format(mData["market_cap_change_24h"])
            market_cap_change_percentage_24h = round(mData["market_cap_change_percentage_24h"],2)
            bot.send_message(
                message.chat.id, f"💰Price Change of {name} *[{symbol}]*\n\n*[24h]*: {c24h}%\n*[7d]*: {c7d}%\n*[30d]*: {c30d}%\n*[200d]*: {c200d}%\n*[1yr]*: {c1y}%\n\nⓂ️Market Cap Change of {name} *[{symbol}]*:\n\n*[24h]*: ${marketcap_change_24h} ({market_cap_change_percentage_24h}%)", parse_mode='Markdown')
        else:
            log_message(f"Get request failed with :{r.status_code}", "error")
            bot.send_message(config['debug_chat_id'], f"Get request failed with :{r.status_code}")
    except Exception as e:
        log_message(e, 'error')
        bot.send_message(config['debug_chat_id'], f"Get request failed with :{e}")
        time.sleep(5)

@bot.message_handler(commands=['rank', 'r'])
def command_rank(message):
    log_message(message, "command")
    try:
        payload = config['market_config']
        r = requests.get(config["url"]+f"coins/{coin}", params=payload)
        if(r.status_code == 200):
            log_message("Fetched market data successfully.", 'info')
            data1 = r.json()
            rank = data1['market_cap_rank']
            payload={"vs_currency": "usd", "page":int(rank/10)+1,"per_page":10}
            r = requests.get(config["url"]+"coins/markets", params=payload)
            if(r.status_code==200):
                log_message("Fetched market list successfully.", 'info')
                data=r.json()
                rank100 = rank-int(rank/10)*10
                data.sort(key=lambda x: x['market_cap_rank'])
                coinsList = data[max(rank100-3,0):min(rank100+2, len(data))]
                msg=f"Market Cap Ranking {name} *[{symbol}]*\n"

                for i in range(len(coinsList)):
                    if(coinsList[i]['symbol'].upper() == data1['symbol'].upper()):
                        if(coinsList[i]['market_cap_rank']==1):
                            msg += f"\n*#{coinsList[i]['market_cap_rank']}* {coinsList[i]['symbol'].upper()} 👑"
                        else:
                            msg += f"\n*#{coinsList[i]['market_cap_rank']}* {coinsList[i]['symbol'].upper()} 🚀"
                    else:
                        msg += f"\n*#{coinsList[i]['market_cap_rank']}* {coinsList[i]['symbol'].upper()}"
                bot.send_message(message.chat.id,msg,parse_mode='Markdown')

        else:
            log_message(f"Get request failed with :{r.status_code}", "error")
            bot.send_message(config['debug_chat_id'], f"Get request failed with :{r.status_code}")

    except Exception as e:
        log_message(e, 'error')
        bot.send_message(config['debug_chat_id'], f"Get request failed with :{e}")
        time.sleep(5)

@bot.message_handler(commands=['sentiment','s'])
def command_sentiment(message):
    log_message(message, "command")
    payload = config['market_config']
    try:
        r = requests.get(config["url"]+f"coins/{coin}", params=payload)
        if(r.status_code==200):
            data = r.json()
            up = data['sentiment_votes_up_percentage']
            down = data['sentiment_votes_down_percentage']
            bot.send_message(message.chat.id,f"Sentiment Today of {name} *[{symbol}]*\n\n{up}% 😄\n{down}% ☹️",parse_mode="Markdown")
        else:
            log_message(f"Get request failed with :{r.status_code}", "error")
            bot.send_message(config['debug_chat_id'], f"Get request failed with :{r.status_code}")

    except Exception as e:
        log_message(e, 'error')
        bot.send_message(config['debug_chat_id'], f"Get request failed with :{e}")
        time.sleep(5)

@bot.message_handler(commands=['stats'])
def command_stats(message):
    log_message(message, "command")
    try:
        r = requests.get(config["elrond_url"])
        if(r.status_code==200):
            data = r.json()
            peak_tps = data['peakTPS']
            total_tx = "{:,}".format(data['totalProcessedTxCount'])
            live_tps = data['liveTPS']
            avg_tps = data['averageTPS']
            round_time = data['roundTime']
            nr_of_shards = data['nrOfShards']
            nr_of_nodes = data['nrOfNodes']
            bot.send_message(message.chat.id,f"{name} Stats\n\n*[Transaction Stats]*\nPeak TPS:{peak_tps}\nLive TPS:{live_tps}\nAvg. TPS: {avg_tps}\nTotal Tx: {total_tx}\n\n*[Network Stats]*\nRound Time: {round_time}s\nNo. Of Shards: {nr_of_shards}\nNo. of Nodes:{nr_of_nodes}",parse_mode="Markdown")
        else:
            log_message(f"Get request failed with :{r.status_code}", "error")
            bot.send_message(config['debug_chat_id'], f"Get request failed with :{r.status_code}")
    except Exception as e:
        log_message(e, 'error')
        bot.send_message(config['debug_chat_id'], f"Get request failed with :{e}")
        time.sleep(5)

"""
--------------------------------------------------------------------------
Helper Functions (Not for telebot to use directly)
--------------------------------------------------------------------------
"""


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


def signal_handler(signal_received, frame):
    log_message("CTRL+c Pressed. Exiting.", "info")
    exit(0)


def main():
    signal(SIGINT, signal_handler)
    while True:
        try:
            log_message("Starting Bot Polling...", "info")
            bot.polling()
        except Exception as e:
            log_message(f"Bot polling error: {e.args}", "error")
            bot.stop_polling()
            time.sleep(10)


if __name__ == "__main__":
    now = time.time()
    logging.basicConfig(filename=f'log/elrondstatsbot/{now}.log',
                        level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    main()
