__author__ = 'Ziyang'

#import  struct
SERVER = 'openapi-contract.coinbene.com'
PORT = 80
HT= 'http://%s/v2/'
HTMRK = '/api/swap/v2/market/'
HTPBL = '/api/swap/v2/market/'
HTORD = '/api/swap/v2/order/'
HTACT = '/api/swap/v2/account/'
HTPOS = '/api/swap/v2/position/'
WS = 'wss://%S/v2/ws/'
base_url = "http://openapi-contract.coinbene.com"

ST = 'server-time'
SYMBOLS = 'symbols'
CURRENCY = 'currencies'
TICKER = 'ticker/%s'

POST = 'POST'
GET = 'GET'

KDATA = 'candles/%s/%s'
KDATA_COLUMNS = ['id', 'open', 'high', 'low', 'close', 'count', 'base_vol', 'quote_vol', 'seq']
KDATA_REAL_COL = ['datetime', 'open', 'high', 'low', 'close', 'count', 'base_vol', 'quote_vol', 'seq']

import requests
import time
import base64
import sys
import hashlib
import hmac
from datetime import datetime
import json
import math



class DataAPI():
    def __init__(self, key='', secret=''):
        self.http = HT
        self.http_public = HTPBL
        self.http_market = HTMRK
        self.http_orders = HTORD
        self.http_account = HTACT
        self.http_position = HTPOS
        self.key = key
        self.secret = bytes(secret,encoding = "utf8")
    def authorize(self, key='', secret=''):
        self.key = key
       # self.secret = bytes(secret,encoding = "utf8")
        self.secret = secret.encode('utf-8')


    def signed_request(self, method, url, **params):
        param = ''
        if params:
            sort_pay = list(params.items())
            sort_pay.sort()
            for k in sort_pay:
                param += '&' + str(k[0]) + '=' + str(k[1])
            param = param.lstrip('&')
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


        if method == GET:
            if param:
                url = url + '?' + param
            sig_str = timestamp+method + url
        elif method == POST:

            sig_str = timestamp +method + url + json.dumps(params)
        #print(sig_str)
        #print("secret",self.secret)

        signature = self.get_signed(sig_str)


        headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
                "Content-Type": "application/json;charset=utf-8", "Connection": "keep-alive",
                "Cookie": "locale=zh_CN",
                 'ACCESS-KEY': self.key,
                 'ACCESS-SIGN': signature,
                 'ACCESS-TIMESTAMP': str(timestamp)
                 }

        #print(headers)
        #print(base_url+url)
        if len(params)==0:
            params=None

        try:
            r = requests.request(method, base_url+url, headers=headers, json=params,timeout=5)
            requests.session().close()
            r.raise_for_status()
        except Exception as err:
            print(r.text)
            print(err)
            return None
        if r.status_code == 200:
            return r.json()

    def public_request(self, method, url, **params):


        #print(url)
        try:
            r = requests.request(method, base_url+url, params=params,timeout=5)
            requests.session().close()
            r.raise_for_status()
        except Exception as err:
            print(err)
            return None
        if r.status_code == 200:
            return r.json()
    def get_two_float(self, price, n):
        f_str = str(price)
        if "e" in f_str:
            f_str = "%f"%(price)
        f_str = str(f_str)  # f_str = '{}'.format(f_str) 也可以转换为字符串
        a, b, c = f_str.partition('.')
        c = (c + "0" * n)[:n]  # 如论传入的函数有几位小数，在字符串后面都添加n为小数0
        return ".".join([a, c])
    def get_signed(self,message):
        """
        gen sign
        :param message: message wait sign
        :param secret:  secret key
        :return:
        """
        message = message.encode('utf-8')
        sign = hmac.new(self.secret, message, digestmod=hashlib.sha256).hexdigest()
        return sign
    '''
    def get_signed(self, sig_str):
        #print(sig_str)
        sig_str = bytes(sig_str,encoding = "utf8")
        sig_str = base64.b64encode(sig_str)
        signature = base64.b64encode(hmac.new(self.secret, sig_str, digestmod=hashlib.sha1).digest())
        return signature
    '''

    def server_time(self):
        return self.public_request(GET, self.http_public + ST)['data']

    def currencies(self):
        return self.public_request(GET, self.http_public + CURRENCY)['data']

    def symbols(self):
        js = self.public_request(GET, "https://www.ifukang.com/openapi/v2/symbols")['data']["symbols"]
        #print(js)
       # df = pd.DataFrame(js)
        return js

    def get_kdata(self, freq='M1', symbol='',limit=1):
        js = self.public_request(GET, self.http_market + KDATA % (freq, symbol),limit=limit)
        return js
    def get_position(self,market):
        """get user balance"""
        return self.signed_request(GET, self.http_position + 'list?symbol='+market)

    def get_balance(self):
        """get user balance"""
        return self.signed_request(GET, self.http_account + 'info')

    def list_orders(self, symbol,states="open"):
        """get orders"""
        if states=="open":
            return self.signed_request(GET, self.http_orders+"openOrders?symbol="+symbol)
        if states=="close":
            return self.signed_request(GET, self.http_orders + "closedOrders?symbol=" + symbol)

    def create_order(self, **payload):
        """create order"""
        return self.signed_request(POST, self.http_orders+"place", **payload)

    def buy(self, symbol, orderPrice, quantity,leverage="2"):
        """buy someting"""
        return self.create_order(symbol=symbol, direction='openLong', orderType='limit', orderPrice=str(orderPrice), quantity=quantity,leverage=leverage)

    def sell(self, symbol, orderPrice, quantity,leverage="2"):
        """sell someting"""
        return self.create_order(symbol=symbol, direction='closeLong', orderType='limit', orderPrice=str(orderPrice), quantity=quantity,leverage=leverage)

    def open_short(self, symbol, orderPrice, quantity,leverage="2"):
        """buy someting"""
        return self.create_order(symbol=symbol, direction='openShort', orderType='limit', orderPrice=str(orderPrice), quantity=quantity,leverage=leverage)
    def close_short(self, symbol, orderPrice, quantity,leverage="2"):
        """buy someting"""
        return self.create_order(symbol=symbol, direction='closeShort', orderType='limit', orderPrice=str(orderPrice), quantity=quantity,leverage=leverage)



    def get_order(self, order_id):
        """get specfic order"""
        return self.signed_request(GET, self.http_orders + "info?orderId="+order_id)

    def cancel_order(self, order_id):
        """cancel specfic order"""

        return self.signed_request(POST, self.http_orders + 'cancel',orderId=order_id)
    def batch_cancel(self,order_list):
        return self.signed_request(POST, self.http_orders + 'batchCancel',orderIds=order_list)

    def order_result(self, order_id):
        """check order result"""
        return self.signed_request(GET, self.http_orders + '%s/match-results' % order_id)

    def get_depth(self, level, symbol):
        """get market depth"""
        return self.public_request(GET, self.http_market + 'orderBook?symbol=%s&size=%s' % (symbol,level))

    def get_trades(self, symbol):
        """get detail trade"""
        return self.public_request(GET, self.http_market + 'trades/%s' % symbol)

    def get_tickers(self):
        return self.public_request(GET, self.http_market + 'tickers')

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

    def get_min_price_tick(self,market):
        self.price_decimal = {"BTCUSDT": 0.5, "ETHUSDT": 0.05, "LTCUSDT": 0.01, "EOSUSDT": 0.001}
        return self.price_decimal.get(market,0.5)

    def set_demical(self):

        self.amount_decimal = {"BTCUSDT":0,"ETHUSDT":0,"LTCUSDT":0,"EOSUSDT":0}
        self.price_decimal = {"BTCUSDT": 0.5, "ETHUSDT": 0.05, "LTCUSDT": 0.01, "EOSUSDT": 0.001}
        self.swap_value = {"BTCUSDT": 1, "ETHUSDT": 0.000001, "LTCUSDT": 0.000003, "EOSUSDT": 0.00005}
        self.limit_amount_min = {"BTCUSDT":1,"ETHUSDT":1,"LTCUSDT":1,"EOSUSDT":1}

        return self.limit_amount_min

    def amount_can_buy(self,market,leverage,available_money,price):
        leverage=float(leverage)
        if market=="BTCUSDT":
            amount = leverage*available_money*price
        else:
            amount = leverage*available_money/(self.swap_value[market]*price)
        return int(amount*0.95)
    def get_depth(self, market):
        # try:
        obj = self._api.get_depth("10",market)
        print(obj)
        return obj.get("data",None)
        #  except Exeption as ex:
        #      print(sys.stderr, 'zb query_account exception,', ex)
        #      return None

    def get_buy1_and_ask1(self,market):
        obj = self._api.get_tickers()
        obj = obj.get("data",dict()).get(market,None)
        if obj==None:
            return 0,0,0,0,0
        else:
            buy1 = float(obj["bestBidPrice"])
            sell1 = float(obj["bestAskPrice"])
            buy1_amount = float(obj["bestBidVolume"])
            ask1_amount=float(obj["bestAskVolume"])
            average = float(obj["volume24h"]) / 24 / 60
            return buy1,buy1_amount, sell1,ask1_amount,average

    def get_two_float(self, price, n):
        f_str = str(price)
        if "e" in f_str:
            f_str = "%f"%(price)
        f_str = str(f_str)  # f_str = '{}'.format(f_str) 也可以转换为字符串
        a, b, c = f_str.partition('.')
        c = (c + "0" * n)[:n]  # 如论传入的函数有几位小数，在字符串后面都添加n为小数0
        return ".".join([a, c])

    def price_format(self,price, precious, mode):
        """
        format the price to meet the request of system
        :param price:  the origin price
        :param precious: the step of price ex:BTCUSDT is 0.5
        :param mode: 1 up or 0down
        :return: price after format
        """
        f, i = math.modf(price)
        r = f // precious
        if mode == 1:
            r = r + 1
        return i + precious * r
    def take_order(self, market, direction, price, size,leverage="2"):
        while True:
            #size = self.get_two_float(size,self.amount_decimal[market])
            #price=self.get_two_float(price,self.price_decimal[market])
            price=self.price_format(price,self.price_decimal[market],1)
            print(direction)
            print(size)
            print(price)
            size = int(size)
            if direction == "buy":
                obj = self._api.buy(symbol=market, orderPrice=price, quantity=size,leverage=leverage)
            elif direction == "sell":
                obj = self._api.sell(symbol=market, orderPrice=price, quantity=size,leverage=leverage)
            elif direction=="openshort":
                obj = self._api.open_short(symbol=market, orderPrice=price, quantity=size,leverage=leverage)
            elif direction=="closeshort":
                obj = self._api.close_short(symbol=market, orderPrice=price, quantity=size,leverage=leverage)
            if obj:
                break
            else:
                time.sleep(1)
                return "-1"

        id = obj.get("data", dict()).get("orderId","-1")
        return id

    def get_order_info(self, market, id):
        obj = self._api.get_order(order_id=id)
        print(obj)
        return obj["data"]

    def is_order_complete(self, market, id):
        obj = self.get_order_info(market, id)
        if obj["status"]=="filled" or "canceled" in obj["status"]:
            return True
        else:
            return False

    def get_total_balance(self):
        obj2 = self._api.get_balance()
        balance = float(obj2.get("data",dict()).get("balance",0))
        return float(balance)


    def get_available_balance(self, market):
        obj1 = self._api.get_position(market)
        obj2 = self._api.get_balance()
        #print(obj1)
        #print(obj2)
        aval_money = float(obj2.get("data",dict()).get("availableBalance",0))
        obj1 = obj1.get("data",None)
        if obj1==None:
            aval_long_coins = [0]
            aval_short_coins=[0]
        else:
            aval_long_coins = [0 if item["side"]=="short" else float(item["availableQuantity"]) for item in obj1]
            aval_short_coins = [0 if item["side"]=="long" else float(item["availableQuantity"]) for item in obj1]

        return aval_money, sum(aval_long_coins),sum(aval_short_coins)

    def get_buy1_and_sell1(self, market):
        obj = self._api.get_tickers()
        obj = obj.get("data",dict()).get(market,None)
        if obj==None:
            obj = self.get_depth(market)
            buy1 = obj["bids"][0][0]
            sell1 = obj["asks"][0][0]
            return buy1, sell1,0
        else:
            buy1 = obj["bestBidPrice"]
            sell1 = obj["bestBidPrice"]
            average = float(obj["volume24h"])/24/60
            return buy1, sell1,average

    def get_filled_amount(self,market,id):
        obj = self.get_order_info(market,id)
        filled_amount = float(obj.get("filledQuantity",0))
        return filled_amount

    def get_level_one_amount(self,market,side,obj=None):
        if not obj:
            obj = self.get_depth(market)
        amount = 0
        for i in range (1,5):
            amount+=float(obj[side][i*2+1])
        return amount
    def get_level_two_amount(self,market,side):
        obj = self.get_depth(market)
        amount = 0
        for i in range (5,15):
            amount+=float(obj[side][i*2+1])
        return amount

    def cancel_all_pending_order(self,market):
        obj = self._api.list_orders(symbol=market,states="open")
        obj = obj["data"]
        id_list = [item["orderId"] for item in obj]
        for id in id_list:
            time.sleep(0.5)
            self.cancel_order(market,id)

    def cancel_all_buy_pending_order(self,market):
        obj = self._api.list_orders(symbol=market,states="open")
        obj = obj["data"]
        for item in obj:
            if item["side"]=="buy":
                self.cancel_order(market,item["id"])

    def cancel_all_sell_pending_order(self,market):
        obj = self._api.list_orders(symbol=market,states="open")
        obj = obj["data"]
        for item in obj:
            if item["side"]=="sell":
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
        try:
            obj = self._api.cancel_order(id)
        except Exception as ex:
            print(sys.stderr, 'in cancel order: ', ex)
            pass
        return obj


'''
market = "EOSUSDT"
leverage=2
api = fcoin_api("72fd87f800bf04c5c38352dc5135bf29","51da7f964e6b4ca391040adc6ddcad43")
api.set_demical()
print(api.get_total_balance())
buy1,buy1_amount,sell1,sell1_amount,average=api.get_buy1_and_ask1(market)
id = api.take_order(market,"buy",sell1*1.01,1)
print(id)
print(api.get_filled_amount(market,id))
'''