__author__ = 'Ziyang'
import threading
import  struct
SERVER = 'api.fcoin.com'
PORT = 80
HT= 'https://%s/v2/'
HTMRK = 'https://%s/v2/market/'
HTPBL = 'https://%s/v2/public/'
HTORD = 'https://%s/v2/orders/'
HTACT = 'https://%s/v2/accounts/'
HBROK = 'https://%s/v2/broker/leveraged_accounts/'
WS = 'wss://%S/v2/ws/'

ST = 'server-time'
SYMBOLS = 'symbols'
CURRENCY = 'currencies'
TICKER = 'ticker/%s'

POST = 'POST'
GET = 'GET'

KDATA = 'candles/%s/%s'
KDATA_COLUMNS = ['id', 'open', 'high', 'low', 'close', 'count', 'base_vol', 'quote_vol', 'seq']
KDATA_REAL_COL = ['datetime', 'open', 'high', 'low', 'close', 'count', 'base_vol', 'quote_vol', 'seq']

import hmac
import hashlib
import pandas as pd
import requests
import time
import base64
import sys


class DataAPI():
    def __init__(self, key='', secret=''):
        self.http = HT % SERVER
        self.http_public = HTPBL % SERVER
        self.http_market = HTMRK % SERVER
        self.http_orders = HTORD % SERVER
        self.http_account = HTACT % SERVER
        self.http_leverage = HBROK % SERVER
        self.key = key
        self.secret = bytes(secret,encoding = "utf8")
        self.mutex = threading.Lock()

        self.sem = threading.Semaphore(5)
    def authorize(self, key='', secret=''):
        self.key = key
        self.secret = bytes(secret,encoding = "utf8")

    def signed_request(self, method, url, **params):
        param = ''
        if params:
            sort_pay = list(params.items())
            sort_pay.sort()
            for k in sort_pay:
                param += '&' + str(k[0]) + '=' + str(k[1])
            param = param.lstrip('&')
        timestamp = str(int(time.time() * 1000))

        if method == GET:
            if param:
                url = url + '?' + param
            sig_str = method + url + timestamp
        elif method == POST:
            sig_str = method + url + timestamp + param

        signature = self.get_signed(sig_str)


        headers = {
            'FC-ACCESS-KEY': self.key,
            'FC-ACCESS-SIGNATURE': signature,
            'FC-ACCESS-TIMESTAMP': timestamp

        }
        #print(url)
        url = url.replace("com", "pro", 1)
        #print(url)

        try:
            with self.sem:
                r = requests.request(method, url, headers=headers, json=params,timeout=5)
            requests.session().close()
            r.raise_for_status()
        except Exception as err:
            print(err)
            print(r.text)
            return dict()
        if r.status_code == 200:
            return r.json()

    def public_request(self, method, url, **params):
        url=url.replace("ifukang", "fcoin", 1)

        #print(url)
        url = url.replace("com", "pro", 1)
        #print(url)
        try:
            with self.sem:
                r = requests.request(method, url, params=params,timeout=5)
            requests.session().close()
            r.raise_for_status()
        except Exception as err:
            print(err)
        if r.status_code == 200:
            return r.json()

    def get_signed(self, sig_str):
        #print(sig_str)
        sig_str = bytes(sig_str,encoding = "utf8")
        sig_str = base64.b64encode(sig_str)
        signature = base64.b64encode(hmac.new(self.secret, sig_str, digestmod=hashlib.sha1).digest())
        return signature

    def server_time(self):
        return self.public_request(GET, self.http_public + ST)['data']

    def currencies(self):
        return self.public_request(GET, self.http_public + CURRENCY)['data']

    def symbols(self):
        js = self.public_request(GET, "https://www.ifukang.com/openapi/v2/symbols")['data']["symbols"]
        #print(js)
        df = pd.DataFrame(js)
        return js

    def get_ticker(self, symbol):
        return self.public_request(GET, self.http_market + TICKER % symbol)

    def get_kdata(self, freq='M1', symbol=''):
        js = self.public_request(GET, self.http_market + KDATA % (freq, symbol))
        df = pd.DataFrame(js['data'])
        df['id'] = df['id'].map(lambda x: int2time(x))
        df = df[KDATA_COLUMNS]
        df.columns = KDATA_REAL_COL
        return df

    def get_balance(self):
        """get user balance"""
        return self.signed_request(GET, self.http_account + 'balance')


    def get_leverage_balance(self):
        """get user balance"""
        return self.signed_request(GET, self.http_leverage )


    def list_orders(self, **payload):
        """get orders"""
        return self.signed_request(GET, self.http_orders, **payload)

    def create_order(self, **payload):
        """create order"""
        return self.signed_request(POST, self.http_orders, **payload)

    def buy(self, symbol, price, amount,exchange="main",account_type=None,type='limit'):
        """buy someting"""
        if account_type=="margin":
            return self.create_order(symbol=symbol, side='buy', type=type, price=str(price), amount=amount,exchange=exchange,account_type=account_type)
        else:
            return self.create_order(symbol=symbol, side='buy', type=type, price=str(price), amount=amount,
                                     exchange=exchange)

    def sell(self, symbol, price, amount,exchange="main",account_type=None,type='limit'):
        """sell someting"""
        if account_type == "margin":
            return self.create_order(symbol=symbol, side='sell', type=type, price=str(price), amount=amount,exchange=exchange,account_type=account_type)
        else:
            return self.create_order(symbol=symbol, side='sell', type=type, price=str(price), amount=amount,
                                     exchange=exchange)

    def get_order(self, order_id):
        """get specfic order"""
        return self.signed_request(GET, self.http_orders + order_id)

    def cancel_order(self, order_id):
        """cancel specfic order"""
        return self.signed_request(POST, self.http_orders + '%s/submit-cancel' % order_id)

    def order_result(self, order_id):
        """check order result"""
        return self.signed_request(GET, self.http_orders + '%s/match-results' % order_id)

    def get_depth(self, level, symbol):
        """get market depth"""
        return self.public_request(GET, self.http_market + 'depth/%s/%s' % (level, symbol))

    def get_trades(self, symbol):
        """get detail trade"""
        return self.public_request(GET, self.http_market + 'trades/%s' % symbol)
    def get_ticker(self,market):
        return  self.public_request(GET, self.http_market+"ticker/"+market)

    def get_huobi_price(self,market):
        return self.public_request(GET,"https://api.huobi.pro/market/detail/merged?symbol="+market)



def int2time(timestamp):
    timestamp = int(timestamp)
    value = time.localtime(timestamp)
    dt = time.strftime('%Y-%m-%d %H:%M:%S', value)
    return dt


class fcoin_api:
    def __init__(self, mykey, mysecret):
        self.mykey = mykey
        self.mysecret = mysecret
        reqTime = (int)(time.time() * 1000)
        self._api = DataAPI(mykey,mysecret )
        #self._ws = fcoin.init_ws()
        self.buy_order = list()
        self.sell_order = list()
        self.current_buy_order = None
        self.current_buy_order = None
        self.amount_decimal = 2
        self.price_decimal = 2
    def get_ticker(self,market):
        obj = self._api.get_ticker(market)
        obj=obj.get("data",dict()).get("ticker",None)
        buy1 = obj[2]
        buy1_amount=obj[3]
        ask1 = obj[4]
        ask1_amount=obj[5]
        average=float(obj[-1])/(24*60)

        return buy1,buy1_amount,ask1,ask1_amount,average


    def get_huobi_price(self,market):
        obj = self._api.get_huobi_price(market)
        #print(obj)
        price = obj.get("tick",dict()).get("close",0)
        return price


    def set_demical(self,money,coins):
        obj = self._api.symbols()
        #obj=obj.loc[(obj['quote_currency'] == money)&(obj['base_currency'] == coin), ['amount_decimal', 'price_decimal',"limit_amount_min"]]
        self.amount_decimal=dict()
        self.price_decimal=dict()
        self.limit_amount_min=dict()
        for coin in coins:
            obj1 = obj[coin+money]
            self.amount_decimal[coin+money] = obj1["amount_decimal"]
            self.price_decimal[coin+money] = obj1["price_decimal"]
            self.limit_amount_min[coin+money] = float(obj1["limit_amount_min"])

        return self.limit_amount_min
    def get_depth(self, market,level="L20"):
        # try:
        obj = self._api.get_depth(level,market)
        return obj.get("data",None)
        #  except Exeption as ex:
        #      print(sys.stderr, 'zb query_account exception,', ex)
        #      return None

    def get_two_float(self, price, n):
        f_str = str(price)
        if "e" in f_str:
            f_str = "%f"%(price)
        f_str = str(f_str)  # f_str = '{}'.format(f_str) 也可以转换为字符串
        a, b, c = f_str.partition('.')
        c = (c + "0" * n)[:n]  # 如论传入的函数有几位小数，在字符串后面都添加n为小数0
        return ".".join([a, c])

    def take_order(self, market, direction, price, size,place="main",account_type=None,type="limit"):
        while True:
            size = self.get_two_float(size,self.amount_decimal[market])
            price=self.get_two_float(price,self.price_decimal[market])
            #print(size)
            #print(price)
            if direction == "buy":
                if account_type=="margin":
                    obj = self._api.buy(symbol=market, price=price, amount=size,exchange=place,account_type=account_type,type=type)
                else:
                    obj = self._api.buy(symbol=market, price=price, amount=size, exchange=place,type=type)
            else:
                if account_type=="margin":
                    obj = self._api.sell(symbol=market, price=price, amount=size,exchange=place,account_type=account_type,type=type)
                else:
                    obj = self._api.sell(symbol=market, price=price, amount=size, exchange=place,type=type)
            #print(obj)
            if obj:
                break
            else:
                time.sleep(1)
                return "-1"

        id = obj.get("data", "-1")
        return id

    def get_order_info(self, market, id):
        obj = self._api.get_order(order_id=id)
        return obj.get("data",None)

    def filled_amount(self,market,id):
        obj = self.get_order_info(market, id)
        return float(obj.get("filled_amount",0))


    def is_order_complete(self, market, id, filled_list=None):
        #print(filled_list)
        if filled_list!=None:
            #print("direct return")
            return (id in filled_list)
        print("search")
        time.sleep(0.2)
        obj = self.get_order_info(market, id)
        if not obj:
            return False
        if obj["state"]=="filled" or "canceled" in obj["state"]:
            return True
        else:
            return False

    def get_available_balance(self, money, coin,type="main"):
        if type=="margin":
            obj = self._api.get_leverage_balance()
            coin_list = obj.get("data",list())
            for item in coin_list:
                if item["leveraged_account_type"]==(coin+money):
                    res_money = float(item["available_quote_currency_amount"])
                    res_freez_money = float(item["frozen_quote_currency_amount"])
                    res_coin = float(item["available_base_currency_amount"])
                    res_freez_coin = float(item["frozen_base_currency_amount"])
        else:
            obj = self._api.get_balance()
            coin_list = obj.get("data",list())
            # print(coin_list)
            for item in coin_list:
                if item["currency"] == money:
                    res_money = float(item["available"])
                    res_freez_money = float(item["frozen"])
                elif item["currency"] == coin:
                    res_coin = float(item["available"])
                    res_freez_coin = float(item["frozen"])

        return res_money, res_coin, res_freez_money, res_freez_coin

    def get_buy1_and_sell_one(self, market):
        obj = self.get_depth(market)
        buy1 = obj["bids"][0]
        sell1 = obj["asks"][0]
        return buy1, sell1
    def get_complete_order_list(self,market,account_type="main"):
        if account_type=="main":
            obj = self._api.list_orders(symbol=market,states="filled")
        else:
            obj = self._api.list_orders(symbol=market, states="filled",account_type=account_type)
        obj = obj.get("data",None)
        if not obj:
            return list()
        id_list  = [item["id"] for item in obj]
        return id_list
    def cancel_all_pending_order(self,market,account_type="main",cancel_list=None):
        if cancel_list==None:
            if account_type=="main":
                obj = self._api.list_orders(symbol=market,states="submitted,partial_filled")
            else:
                obj = self._api.list_orders(symbol=market, states="submitted,partial_filled",account_type=account_type)
            #print(obj)
            obj = obj.get("data",None)
            if not obj:
                return
            id_list = [item["id"] for item in obj]
        else:
            id_list = cancel_list
        for id in id_list:
            #time.sleep(0.5)
            self.cancel_order(market,id)

    def list_all_orders(self,market,account_type="main"):
        if account_type=="main":
            obj = self._api.list_orders(symbol=market,states="submitted,partial_filled,partial_canceled,filled,canceled")
        else:
            obj = self._api.list_orders(symbol=market, states="submitted,partial_filled,partial_canceled,filled,canceled",account_type=account_type)
        print(obj)
        obj = obj["data"]
        return obj

    def cancel_all_buy_pending_order(self,market,account_type="main"):
        if account_type=="main":
            obj = self._api.list_orders(symbol=market,states="submitted,partial_filled")
        else:
            obj = self._api.list_orders(symbol=market, states="submitted,partial_filled",account_type=account_type)
        print(obj)
        obj = obj["data"]
        for item in obj:
            if item["side"]=="buy":
                self.cancel_order(market,item["id"])

    def cancel_all_sell_pending_order(self,market,account_type="main"):
        if account_type=="main":
            obj = self._api.list_orders(symbol=market,states="submitted,partial_filled")
        else:
            obj = self._api.list_orders(symbol=market, states="submitted,partial_filled",account_type=account_type)
        print(obj)
        obj = obj["data"]
        for item in obj:
            if item["side"]=="sell":
                self.cancel_order(market,item["id"])


    def cancel_all_pending_order_larger_1_hour(self,market):
        obj = self._api.list_orders(symbol=market,states="submitted,partial_filled")
        print(obj)
        obj = obj["data"]
        obj1 = self.get_depth(market)
        ask1 = obj1["asks"][0 * 2]
        buy1 = obj1["bids"][0 * 2]
        current_time = time.time()
        for item in obj:
            created_time=int(item["created_at"])
            print(created_time)
            if current_time - int(item["created_at"])>3600:
                side =item["side"]
                if (side=="buy" and item["price"]<buy1-buy1*0.2)or(side=="sell" and item["price"]>ask1+ask1*0.2):
                    time.sleep(0.1)
                    self.cancel_order(market,item["id"])
    def cancel_all_pending_order_larger_5_min(self,market):
        obj = self._api.list_orders(symbol=market,states="submitted,partial_filled")
        print(obj)
        obj = obj["data"]
        obj1 = self.get_depth(market)
        ask1 = obj1["asks"][0 * 2]
        buy1 = obj1["bids"][0 * 2]
        current_time = time.time()
        for item in obj:
            created_time=int(item["created_at"])
            print(created_time)
            if current_time - int(item["created_at"])>300:
                side =item["side"]
                if (side=="buy" and item["price"]<buy1-buy1*0.2)or(side=="sell" and item["price"]>ask1+ask1*0.2):
                    time.sleep(0.1)
                    self.cancel_order(market,item["id"])



    def get_pending_money(self,market):
        obj = self._api.list_orders(symbol=market,states="submitted,partial_filled")
        obj = obj["data"]
        money = 0
        for item in obj:
            money += float(item["price"])*(float(item["amount"]) - float(item["filled_amount"]))
        return money


    def cancel_order(self, market, id):
        if id=="-1":
            return None
        obj = self._api.cancel_order(id)
        return obj


    def get_total_balance(self):
        obj = self._api.get_balance()
        coin_list = obj["data"]
        #print(coin_list)
        money =0
        for item in coin_list:
            coin = item["currency"]
            available = float(item["available"])
            frozen = float(item["frozen"])
            if available<0.0001 and frozen<0.0001:
                continue
            else:
                time.sleep(0.5)
                if coin=="usdt":
                    buy1=1
                else:
                    buy1,_=self.get_buy1_and_sell_one(coin+"usdt")
                money+=(available+frozen)*buy1

        return money

        return res_money, res_coin, res_freez_money, res_freez_coin


    '''
    def balance_account(self,money,coin):
        buy,ask = api.get_buy1_and_sell_one(market)
        avail_money,avail_coin,freez_money,freez_coin = api.get_available_balance(money,coin)
        ratio = (avail_money+freez_money)/(avail_money+freez_money+(avail_coin+freez_coin)*buy)
        print("ratio:%f" % ratio)
        while(ratio>0.52 or ratio<0.48):
            buy, ask = api.get_buy1_and_sell_one(market)
            avail_money,avail_coin,freez_money,freez_coin = api.get_available_balance(money, coin)
            ratio = (avail_money+freez_money)/(avail_money+freez_money+(avail_coin+freez_coin)*buy)
            print("ratio:%f" % ratio)
            if ratio<0.48:
                sell_order_id = api.take_order(market, "sell", buy, size=1)
                time.sleep(2)
                if not api.is_order_complete(market,sell_order_id):
                    api.cancel_order(market,sell_order_id)
            elif ratio>0.52:
                buy_order_id = api.take_order(market, "buy", ask, size=1)
                time.sleep(2)
                if not api.is_order_complete(market,buy_order_id):
                    api.cancel_order(market,buy_order_id)

    '''

    def balance_account(self, money, coin,market):
        buy, ask = self.get_buy1_and_sell_one(market)
        avail_money, avail_coin, freez_money, freez_coin = self.get_available_balance(money, coin)
        ratio = (avail_money + freez_money) / (avail_money + freez_money + (avail_coin + freez_coin) * buy)
        print("ratio:%f" % ratio)
        if ratio < 0.48:
            sell_size = ((avail_money + avail_coin * buy) * 0.5 - avail_money) / ask
            self.take_order(market, "sell", ask, size=sell_size)
        elif ratio > 0.52:
            buy_size = (avail_money - (avail_money + avail_coin * buy) * 0.5) / buy
            self.take_order(market, "buy", buy, size=buy_size)

        while True:
            time.sleep(2.001)
            obj = self.get_pending_orders(market)
            print(obj)
            if isinstance(obj, dict):
                break

    def wait_pending_order(self, market):
        while True:
            time.sleep(2.001)
            obj = self.get_pending_orders(market)
            print(obj)
            if isinstance(obj, dict):
                break

    def enqueue_sell_order(self, price, size):
        self.sell_order.append((price, size))
        self.sell_order.sort(key=lambda a: a[0], reverse=False)
        self.current_sell_order = (price, size)

    def enqueue_buy_order(self, price, size):
        self.buy_order.append((price, size))
        self.buy_order.sort(key=lambda a: a[0], reverse=True)
        self.current_buy_order = (price, size)

    def dequeue_current_sell_order(self):
        if self.current_sell_order:
            self.sell_order.remove(self.current_sell_order)
            self.current_sell_order = None

    def dequeue_current_buy_order(self):
        if self.current_buy_order:
            self.buy_order.remove(self.current_buy_order)
            self.current_buy_order = None

    def handle_order_in_queue(self, market):
        print("handling sell_orders and buy orders in queue")
        for i, item in enumerate(self.sell_order):
            time.sleep(1)
            money, coin, freez_money, freez_coin = self.get_available_balance("usdt", "tusd")
            buy, ask = self.get_buy1_and_sell_one(market)
            price = item[0]
            size = item[1]
            if coin >= size:
                price = max(price,ask)
                self.take_order(market=market, direction="sell", price=price, size=size)
                continue
            else:
                self.sell_order = self.sell_order[i:]
                break

        for i, item in enumerate(self.buy_order):
            time.sleep(1)
            money, coin, freez_money, freez_coin = self.get_available_balance("usdt", "tusd")
            buy, ask = self.get_buy1_and_sell_one(market)
            price = item[0]
            size = item[1]
            if money >= price * size:
                price = min(buy,price)
                self.take_order(market=market, direction="buy", price=price, size=size)
                continue
            else:
                self.buy_order = self.buy_order[i:]
                break

    def create_cells(self, upper_price, lower_price, middle_price, total_coin, cell_num):
        price_per_cell = (upper_price - lower_price) / cell_num
        upper_half_cell_num = int((upper_price - middle_price) / price_per_cell)
        lower_half_cell_num = cell_num - upper_half_cell_num
        money_for_each_area = total_coin / 2
        base = 0
        d_for_upper_area = 2 * (money_for_each_area - base) / (upper_half_cell_num * (upper_half_cell_num - 1))
        base = money_for_each_area + (upper_half_cell_num) * d_for_upper_area
        d_for_lower_area = 2 * (total_coin - base) / (lower_half_cell_num * (lower_half_cell_num - 1))
        self.cell_money = list()
        self.cell_step = list()
        base = 0
        for i in range(upper_half_cell_num):
            if i == 0:
                self.cell_money.append(base)
            else:
                self.cell_money.append(self.cell_money[-1] + d_for_upper_area * (i + 1))
            self.cell_step.append(d_for_upper_area * (i + 1))
        base = money_for_each_area + (upper_half_cell_num) * d_for_upper_area
        for i in range(lower_half_cell_num):
            if i == 0:
                self.cell_money.append(base)
            else:
                self.cell_money.append(self.cell_money[-1] + d_for_lower_area * (lower_half_cell_num - i))
            self.cell_step.append(d_for_lower_area * (lower_half_cell_num - i))

        print(self.cell_step)
        print(self.cell_money)

    def compute_current_num_of_coin_should_have(self, upper_price, lower_price, cell_num, current_price):
        if current_price <= lower_price:
            return self.cell_money[-1]
        if current_price >= upper_price:
            return 0
        index = int(((upper_price - current_price) / (upper_price - lower_price)) * cell_num)
        # print("current_price:%f" % current_price)
        # print("index:%d" % index)
        # print("coin_should_have:%f" % self.cell_money[index])
        return self.cell_money[index]

    def compute_current_num_coin_step(self, upper_price, lower_price, cell_num, current_price):
        if current_price <= lower_price:
            return 0
        if current_price >= upper_price:
            return 0
        index = int(((upper_price - current_price) / (upper_price - lower_price)) * cell_num)
        # print("current_price:%f" % current_price)
        # print("index:%d" % index)
        # print("coin_should_have:%f" % self.cell_money[index])
        return 5*(self.cell_step[index])

'''
api = fcoin_api("1","2")
print(api.get_huobi_price("btcusdt"))
print(api.get_ticker("btcusdt")[0])
'''
