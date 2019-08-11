import rsa
from base64 import b64encode, b64decode
import os
import uuid
from fcoin_api import  *
import threading
import base64
from multiprocessing import Process
import multiprocessing

import random
import socket


'''
采用AES对称加密算法
'''
# str不是16的倍数那就补足为16的倍数
def add_to_16(value):
    while len(value) % 16 != 0:
        value += '\0'
    return str.encode(value)  # 返回bytes
#加密方法
def encrypt_oracle(text):
    # 秘钥
    key = 'fhkgg'
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    #先进行aes加密
    encrypt_aes = aes.encrypt(add_to_16(text))
    #用base64转成字符串形式
    encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
    return(encrypted_text)
#解密方法
def decrypt_oralce(text):
    # 秘钥
    key = 'fhkgg'
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    #优先逆向解密base64成bytes
    base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))
    #执行解密密并转码返回str
    decrypted_text = str(aes.decrypt(base64_decrypted),encoding='utf-8').replace('\0','')
    return(decrypted_text)



class Section:
#粘贴的回调函数
    def onPaste(self):
        try:
            self.text = win.clipboard_get()
            #获得系统粘贴板内容
        except tkinter.TclError:
            pass
        #防止因为粘贴板没有内容报错
        show.set(str(self.text))
        #在文本框中设置刚刚获得的内容

    def onPaste1(self):
        try:
            self.text = win.clipboard_get()
            #获得系统粘贴板内容
        except tkinter.TclError:
            pass
        #防止因为粘贴板没有内容报错
        show1.set(str(self.text))
        #在文本框中设置刚刚获得的内容

    def onPaste2(self):
        try:
            self.text = win.clipboard_get()
            #获得系统粘贴板内容
        except tkinter.TclError:
            pass
        #防止因为粘贴板没有内容报错
        show2.set(str(self.text))
        #在文本框中设置刚刚获得的内容

#复制的回调函数
    def onCopy(self):
        self.text = T.get(1.0,tkinter.END)
        #获得文本框内容
        win.clipboard_append(self.text)
        #添加至系统粘贴板


def get_mac_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    #print(s.getsockname()[0])
    return (s.getsockname()[0])
   # node = uuid.getnode()
   # mac = uuid.UUID(int = node).hex[-12:]
   # return mac

def check_and_save(signature):
    #signature = entry1.get().strip().encode()
    #print("Signature")
    #print(signature)
    new_msg = msg1+gap+"lyaegjdfuyeu"
    try:
        rsa.verify(new_msg.encode(), b64decode(signature), public)
    except:
        print("wrong license!!!")
        a = input("")
        sys.exit()
    with open(yanzheng_file_name, 'w') as f:
        f.write(encrypt_oracle(msg1+":::::"+signature.decode()))
        #f.write("\n")
        #f.write(encrypt_oracle(signature.decode()))
        #f.write(msg1+"\n")
        #f.write(signature.decode())
    win.destroy()


def buy_main_body(mutex2,api,bidirection,partition,_money,_coin,min_size,money_have,coin_place,trade_type="margin"):
    need_balance = False
    cell_num = 20
    market = _coin + _money
    stamp = int(time.time())
    time_local = time.localtime(stamp)
    new_hour = int(time_local.tm_hour)
    min_price_tick = 1 / (10 ** api.price_decimal[market])
    small_trade=False if "eth" in market or "ltc" in market or "btc" in market else True
    begin_time = time.time()
    real_time_price_list=list()
    while True:
        try:
            obj = api.get_depth(market)
            ask1 = obj["asks"][0 * 2]
            buy1 = obj["bids"][0 * 2]
            money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin, trade_type)
            init_value = (money + freez_money) + (coin + freez_coin) * buy1
            break
        except:
            continue

    tolerant_loss=init_value*0.004
    huge_loss=init_value*0.01
    huge_profit=init_value*0.01
    profit_step=min_price_tick*1

    if trade_type=="margin":
        money_have = sys.maxsize
    if new_hour == 0:
        daily_restart = True
    else:
        daily_restart = False
    while True:
        try:

            print("in init market")
            price_list = list()
            sell_order_list = list()
            buy_order_list = list()
            tmp_buy_order_list = list()
            tmp_sell_order_list = list()

            api.cancel_all_pending_order(market,trade_type)

            obj = api.get_depth(market)
            ask1 = obj["asks"][0 * 2]
            buy1 = obj["bids"][0 * 2]
            #min_price_tick = 0.005*buy1
            if trade_type=="margin":
                money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin, trade_type)
                current_value = (money + freez_money) + (coin + freez_coin) * buy1
                if init_value-current_value>huge_loss:
                    cell_num = 100
                    profit_step = 10 * min_price_tick
                    api.take_order(market, "sell", buy1*0.95, coin, coin_place, trade_type)
                else:
                    cell_num = 20
                    profit_step = 2*min_price_tick

            lowest_buy = buy1
            higest_ask = ask1

            #print("trade_pair:%s" % (market))

            price_step = min_price_tick
            if "btc" in market:
                price_step = 5*min_price_tick
            if "eth" in market or "ltc" in market:
                price_step = 2*min_price_tick

            base_price = buy1 - (cell_num / 2) * price_step

            for i in range(cell_num):
                price = base_price + price_step*i
                price_list.append(price)
            if max(price_list) < ask1:
                gap = 100
            elif min(price_list) > ask1:
                gap = 0
            else:
                gap = 99
                for i in range(len(price_list) - 1):
                    if price_list[i] < ask1 and price_list[i + 1] >= ask1:
                        gap = i
                        break
                gap += 1
            #print("gap:%d" % gap)

            coin_need = coin
            sell_order_num = len(price_list[gap:])
            min_money_need_for_sell = 0
            if sell_order_num==0:
                sell_step=min_size
            else:
                sell_step = max(coin_need/sell_order_num,min_size)
            '''

            if gap < cell_num:

                for price in price_list[gap:]:
                    min_money_need_for_sell += price * min_size

                money_for_sell = (len(price_list[gap:]) / cell_num) * min(money_have, money + coin * buy1)

                coin_need = (
                                        money_for_sell / min_money_need_for_sell) * min_coin_need if min_money_need_for_sell > 0 else 0
                print("coin need:", coin_need)

            if need_balance:
                if remain_coin - coin_need > 2 * min_size:
                    api.take_order(market, "sell", buy1 - buy1 * 0.01, remain_coin - coin_need - min_size, coin_place,trade_type)
                elif remain_coin < coin_need:
                    api.take_order(market, "buy", ask1 + ask1 * 0.01, coin_need - remain_coin + min_size, coin_place,trade_type)
            time.sleep(1)
            

            money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin,trade_type)
            sell_step = max((coin / len(price_list[gap:])) + 1 / (10 ** api.amount_decimal[market]), min_size)
            '''
            #print("sell step:", sell_step)

            new_list = list()
            buy_step = 0

            if gap > 0:
                new_list = price_list[:gap]
                new_list.reverse()
                min_money_need_for_buy = 0
                # print(new_list)
                money_for_buy = min(money_have, money)
                #print(money_for_buy)
                for price in new_list:
                    min_money_need_for_buy += price * min_size

                if money_for_buy >= min_money_need_for_buy:
                    buy_step = (money_for_buy / min_money_need_for_buy) * min_size + 1 / (
                                10 ** api.amount_decimal[market])
                else:
                    buy_step = min_size
            #print("buy_step:", buy_step)
            _counter=0
            for price in new_list:
                time.sleep(0.5)
                if price < ask1:
                    size = buy_step
                    id = api.take_order(market, "buy", price, size, coin_place,trade_type)
                    if id != "-1":
                        lowest_buy = price
                        _counter = 0
                        buy_order_list.append(
                            {"id": id, "pair": (market, "sell", price + profit_step, size, coin_place),
                             "self": (market, "buy", price, size, coin_place)})
                    else:
                        _counter +=1
                        if _counter>=3:
                            break
            _counter = 0
            if gap < cell_num:
                for price in price_list[gap:]:
                    time.sleep(0.5)
                    if price > ask1:
                        size = sell_step
                        id = api.take_order(market, "sell", price, size, coin_place,trade_type)
                        if id != "-1":
                            higest_ask = price
                            _counter = 0
                            sell_order_list.append(
                                {"id": id, "pair": (market, "buy", price - profit_step, size, coin_place),
                                 "self": (market, "sell", price, size, coin_place)})
                        else:
                            _counter += 1
                            if _counter >= 3:
                                break



        except Exception as ex:
            print(sys.stderr, 'in init: ', ex)
            print("exception")
            continue

        level1_sell_order_list = list()
        level1_buy_order_list = list()
        level1_tmp_buy_order_list = list()
        level1_tmp_sell_order_list = list()
        _start_time = time.time()
        while True:
            try:

                obj = api.get_depth(market)
                ask1 = obj["asks"][0 * 2]
                buy1 = obj["bids"][0 * 2]
                ask10 = obj["asks"][9 * 2]
                buy10 = obj["bids"][9 * 2]

                if len(real_time_price_list)>60:
                    real_time_price_list.remove(real_time_price_list[0])
                    real_time_price_list.append(buy1)
                else:
                    real_time_price_list.append(buy1)

                #risk control
                if (buy1-min(real_time_price_list))/min(real_time_price_list)>0.03:
                    print(market,"bull!!!!!")
                    api.cancel_all_pending_order(market,trade_type)
                    money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin, trade_type)
                    price = ask1*1.05
                    amount = money/price
                    api.take_order(market, "buy", price, amount, coin_place, trade_type)
                    continue
                elif (max(real_time_price_list)-buy1)/buy1>0.03:
                    print(market,"bear!!!!!")
                    api.cancel_all_pending_order(market,trade_type)
                    money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin, trade_type)
                    price = buy*0.95
                    amount=coin
                    api.take_order(market, "sell", price, amount, coin_place, trade_type)
                    continue


                if higest_ask<buy1-(10*min_price_tick) or lowest_buy>ask1+(10*min_price_tick):
                    break
                #print("current ask:%f" % ask1)
                #print("current buy:%f" % buy1)
                #print("trade_pair:%s" % market)
                #print("time spent:%f seconds" % (time.time() - _start_time))
                #print("len of buy_order_list:", len(buy_order_list))

                complete_order_list=api.get_complete_order_list(market,trade_type)
                complete_order_list.append("-1")

                if len(buy_order_list) > 0:
                    buy_item = buy_order_list[0]
                    buy_id_to_monitor = buy_item["id"]
                    time.sleep(1)
                    while api.is_order_complete(market, buy_id_to_monitor,complete_order_list):
                        time.sleep(1)
                        _market = buy_item["pair"][0]
                        _direction = buy_item["pair"][1]
                        _price = buy_item["pair"][2]
                        _size = buy_item["pair"][3]
                        _coin_place = buy_item["pair"][4]
                        id = api.take_order(_market, _direction, _price, _size, _coin_place,trade_type)
                        if id != "-1":
                            tmp_sell_order_list.insert(0,
                                                       {"id": id, "pair": buy_item["self"], "self": buy_item["pair"]})
                        buy_order_list.remove(buy_item)
                        if len(buy_order_list)==0:
                            break
                        buy_item = buy_order_list[0]
                        buy_id_to_monitor = buy_item["id"]
                #print("len of sell order list:", len(sell_order_list))
                if len(sell_order_list) > 0:
                    sell_item = sell_order_list[0]
                    sell_id_to_monitor = sell_item["id"]
                    time.sleep(1)
                    while api.is_order_complete(market, sell_id_to_monitor,complete_order_list):
                        time.sleep(1)
                        _market = sell_item["pair"][0]
                        _direction = sell_item["pair"][1]
                        _price = sell_item["pair"][2]
                        _size = sell_item["pair"][3]
                        _coin_place = sell_item["pair"][4]
                        id = api.take_order(_market, _direction, _price, _size, _coin_place,trade_type)
                        if id != "-1":
                            tmp_buy_order_list.insert(0,
                                                      {"id": id, "pair": sell_item["self"], "self": sell_item["pair"]})
                        sell_order_list.remove(sell_item)
                        if len(sell_order_list)==0:
                            break
                        sell_item = sell_order_list[0]
                        sell_id_to_monitor = sell_item["id"]

                if len(tmp_buy_order_list) > 0:
                    tmp_buy_item = tmp_buy_order_list[0]
                    tmp_buy_id = tmp_buy_item["id"]
                    time.sleep(1)
                    while api.is_order_complete(market, tmp_buy_id,complete_order_list):
                        time.sleep(1)
                        _market = tmp_buy_item["pair"][0]
                        _direction = tmp_buy_item["pair"][1]
                        _price = tmp_buy_item["pair"][2]
                        _size = tmp_buy_item["pair"][3]
                        _coin_place = tmp_buy_item["pair"][4]
                        id = api.take_order(_market, _direction, _price, _size, _coin_place,trade_type)
                        if id != "-1":
                            sell_order_list.insert(0, {"id": id, "pair": tmp_buy_item["self"],
                                                       "self": tmp_buy_item["pair"]})
                        tmp_buy_order_list.remove(tmp_buy_item)
                        if len(tmp_buy_order_list)==0:
                            break
                        tmp_buy_item = tmp_buy_order_list[0]
                        tmp_buy_id = tmp_buy_item["id"]

                if len(tmp_sell_order_list) > 0:
                    tmp_sell_item = tmp_sell_order_list[0]
                    tmp_sell_id = tmp_sell_item["id"]
                    time.sleep(1)
                    while api.is_order_complete(market, tmp_sell_id,complete_order_list):
                        time.sleep(1)
                        _market = tmp_sell_item["pair"][0]
                        _direction = tmp_sell_item["pair"][1]
                        _price = tmp_sell_item["pair"][2]
                        _size = tmp_sell_item["pair"][3]
                        _coin_place = tmp_sell_item["pair"][4]
                        id = api.take_order(_market, _direction, _price, _size, _coin_place,trade_type)
                        if id != "-1":
                            buy_order_list.insert(0, {"id": id, "pair": tmp_sell_item["self"],
                                                      "self": tmp_sell_item["pair"]})
                        tmp_sell_order_list.remove(tmp_sell_item)
                        if len(tmp_sell_order_list)==0:
                            break
                        tmp_sell_item = tmp_sell_order_list[0]
                        tmp_sell_id = tmp_sell_item["id"]


                if len(level1_buy_order_list) > 0:
                    buy_item = level1_buy_order_list[0]
                    buy_id_to_monitor = buy_item["id"]
                    time.sleep(0.25)
                    while api.is_order_complete(market, buy_id_to_monitor,complete_order_list):
                        time.sleep(1)
                        _market = buy_item["pair"][0]
                        _direction = buy_item["pair"][1]
                        _price = buy_item["pair"][2]
                        _size = buy_item["pair"][3]
                        _coin_place = buy_item["pair"][4]
                        id = api.take_order(_market, _direction, _price, _size, _coin_place, trade_type)
                        if id != "-1":
                            level1_tmp_sell_order_list.insert(0,
                                                       {"id": id, "pair": buy_item["self"], "self": buy_item["pair"]})
                        level1_buy_order_list.remove(buy_item)
                        if len(level1_buy_order_list)==0:
                            break
                        buy_item = level1_buy_order_list[0]
                        buy_id_to_monitor = buy_item["id"]
                #print("len of sell order list:", len(sell_order_list))
                if len(level1_sell_order_list) > 0:
                    sell_item = level1_sell_order_list[0]
                    sell_id_to_monitor = sell_item["id"]
                    time.sleep(1)
                    while api.is_order_complete(market, sell_id_to_monitor,complete_order_list):
                        _market = sell_item["pair"][0]
                        _direction = sell_item["pair"][1]
                        _price = sell_item["pair"][2]
                        _size = sell_item["pair"][3]
                        _coin_place = sell_item["pair"][4]
                        id = api.take_order(_market, _direction, _price, _size, _coin_place, trade_type)
                        if id != "-1":
                            level1_tmp_buy_order_list.insert(0,
                                                      {"id": id, "pair": sell_item["self"], "self": sell_item["pair"]})
                        level1_sell_order_list.remove(sell_item)
                        if len(level1_sell_order_list)==0:
                            break
                        sell_item = level1_sell_order_list[0]
                        sell_id_to_monitor = sell_item["id"]

                if len(level1_tmp_buy_order_list) > 0:
                    tmp_buy_item = level1_tmp_buy_order_list[0]
                    tmp_buy_id = tmp_buy_item["id"]
                    time.sleep(1)
                    while api.is_order_complete(market, tmp_buy_id,complete_order_list):
                        _market = tmp_buy_item["pair"][0]
                        _direction = tmp_buy_item["pair"][1]
                        _price = tmp_buy_item["pair"][2]
                        _size = tmp_buy_item["pair"][3]
                        _coin_place = tmp_buy_item["pair"][4]
                        id = api.take_order(_market, _direction, _price, _size, _coin_place, trade_type)
                        if id != "-1":
                            level1_sell_order_list.insert(0, {"id": id, "pair": tmp_buy_item["self"],
                                                       "self": tmp_buy_item["pair"]})
                        level1_tmp_buy_order_list.remove(tmp_buy_item)
                        if len(level1_tmp_buy_order_list)==0:
                            break
                        tmp_buy_item = level1_tmp_buy_order_list[0]
                        tmp_buy_id = tmp_buy_item["id"]

                if len(level1_tmp_sell_order_list) > 0:
                    tmp_sell_item = level1_tmp_sell_order_list[0]
                    tmp_sell_id = tmp_sell_item["id"]
                    time.sleep(0.25)
                    while api.is_order_complete(market, tmp_sell_id,complete_order_list):
                        time.sleep(1)
                        _market = tmp_sell_item["pair"][0]
                        _direction = tmp_sell_item["pair"][1]
                        _price = tmp_sell_item["pair"][2]
                        _size = tmp_sell_item["pair"][3]
                        _coin_place = tmp_sell_item["pair"][4]
                        id = api.take_order(_market, _direction, _price, _size, _coin_place, trade_type)
                        if id != "-1":
                            level1_buy_order_list.insert(0, {"id": id, "pair": tmp_sell_item["self"],
                                                      "self": tmp_sell_item["pair"]})
                        level1_tmp_sell_order_list.remove(tmp_sell_item)
                        if len(level1_tmp_sell_order_list)==0:
                            break
                        tmp_sell_item = level1_tmp_sell_order_list[0]
                        tmp_sell_id = tmp_sell_item["id"]


                money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin, trade_type)

                current_value = (money + freez_money) + (coin + freez_coin) * buy1
                if trade_type=="margin":
                    print("trade_pair:",market,"value loss:",init_value-current_value)
                print(market,"time spent:",time.time()-begin_time)
                if trade_type=="margin" and small_trade and init_value-current_value<tolerant_loss:# and init_value-current_value>-1*tolerant_loss:
                    small_step=3*min_size
                    if money/buy1>small_step:
                        id = api.take_order(market, "buy", buy1, small_step, coin_place, trade_type)
                        if id != "-1":
                            level1_buy_order_list.append(
                                {"id": id, "pair": (market, "sell", buy1 + profit_step, small_step, coin_place),
                                 "self": (market, "buy", buy1, small_step, coin_place)})
                    if coin>small_step:
                        id = api.take_order(market, "sell", ask1, small_step, coin_place, trade_type)
                        if id != "-1":
                            level1_sell_order_list.append(
                                {"id": id, "pair": (market, "buy", ask1 - profit_step, small_step, coin_place),
                                 "self": (market, "sell", ask1, small_step, coin_place)})


            except Exception as ex:
                print(sys.stderr, 'in monitor: ', ex)
                print("restart in 5 seconds......")
                time.sleep(5)

def load_record():
    global load_access_key,load_access_secret,load_money,load_coin,load_parition,load_total_money,load_bidirection,load_coin_place
    with open(config_file, 'r') as f:
        tmp = f.read()
        tmp = decrypt_oralce(tmp)
        parameters = tmp.split(gap)
        load_access_key = parameters[0]
        load_access_secret = parameters[1]
        load_money = parameters[2]
        load_coin = parameters[3]
        load_parition = parameters[4]
        load_total_money = parameters[5]
        load_bidirection = parameters[6]
        load_coin_place = parameters[7]




def tick(load_access_key, load_access_secret, load_money, load_coin, load_parition, load_total_money, load_bidirection, load_coin_place,account_type="main"):
    try:
        mutex2 = threading.Lock()
        access_key = load_access_key.strip()
        access_secret = load_access_secret.strip()
        _money =load_money.strip().lower()
        tmp =load_coin.strip().lower()
        if " "in tmp:
            coins =tmp.split(" ")
        else:
            coins = [tmp]
        markets = [_coin+_money for _coin in coins]
        print(markets)
        partition = int(load_parition.strip())
        assert(partition!=0)
        money_have = float(load_total_money.strip())


        market_exchange_dict = {"bbgcusdt":"renren","btmusdt":"jingxuanremenbi","zipusdt":"servicex","fiusdt":"fiofficial","dogeusdt":"tudamu","aeusdt":"servicex","zrxusdt":"tudamu","batusdt":"jiucai","linkusdt":"jingxuanremenbi","icxusdt":"allin","omgusdt":"ninthzone","zilusdt":"langchao"}

        bidirection=int(load_bidirection.strip())
        coin_place_list = [market_exchange_dict.get(item,"main") for item in markets]



        api = fcoin_api(access_key, access_secret)
        min_size=api.set_demical(_money, coins)
        print("start cancel existing pending orders")
        for market in markets:
            time.sleep(0.1)
            api.cancel_all_pending_order(market,account_type)
        print("cancel pending orders completed")
        for i, market in enumerate(markets):
            time.sleep(0.1)
            thread = threading.Thread(target=buy_main_body,args=(mutex2,api,bidirection,partition,_money,coins[i],min_size[market],money_have/len(markets),coin_place_list[i],account_type))
            thread.setDaemon(True)
            thread.start()
        time.sleep(10800)
        print("tick exit!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    except Exception as ex:
        print(sys.stderr, 'tick: ', ex)
        #a= input()


def save_record():
    global global_config,load_access_key,load_access_secret,load_money,load_coin,load_parition,load_total_money,load_bidirection,load_coin_place

    load_access_key=save_access_key = entry1.get().strip()
    load_access_secret=save_access_secret = entry2.get().strip()
    load_money=save__money = entry4.get().strip().lower()
    load_coin=save__coin = entry5.get().strip().lower()
    load_parition=save_parition = entry6.get().strip()
    load_total_money=save_total_money = (entry7.get().strip())
    load_bidirection=save_bidirection = (entry8.get().strip())
    load_coin_place=save_coin_place = (entry9.get().strip())

    tmp = save_access_key + gap + save_access_secret + gap + save__money + gap + save__coin + gap + save_parition + gap + save_total_money + gap + save_bidirection + gap + save_coin_place
    global_config = encrypt_oracle(tmp)


    with open(config_file, 'w') as f:
        f.write(global_config)


    win.destroy()

def delete_record():
    if os.path.exists(config_file):
        os.remove(config_file)


def is_need_record():

    label1 = tkinter.Label(win, text="是否记住本次配置便于下次重启或多开？:")
    label1.pack()
    button1 = tkinter.Button(win, text="是", command=save_record)  # 收到消息执行这个函数
    button1.pack()  # 加载到窗体，
    button2 = tkinter.Button(win, text="否", command=delete_record)  # 收到消息执行这个函数
    button2.pack()  # 加载到窗体，

def get_license_day():
    global license_day
    license_day = float(entryday.get().strip())
    #license_day  = 0.00069
    win.destroy()
# 导入密钥
labela=None
labelb=None
labelc=None
counter=0

def check_status():
    global win,tran_id,tran,msg1,gap,button,recv_address,amount,labela,labelc,labelb,counter
    token_address="0x7dd8d8f4ef294cd417d17a9ea6c4a0fb146d90b5"
    counter+=1
    if labela:
        labela.destroy()
        labela=None
    if labelb:
        labelb.destroy()
        labelb = None
    if labelc:
        labelc.destroy()
        labelc = None
    labela = tkinter.Label(win, text="操作次数：%d,请等待网络确认:"%(counter))
    labela.pack()
    new_msg = msg1 + gap + "lyaegjdfuyeu"
    tran_id = tran.get().strip()
    URL ="http://api.ethplorer.io/getTxInfo/"+tran_id+"?apiKey=freekey"
    print("tran_id:%s" % tran_id)
    r = requests.request("GET", URL)
    r.raise_for_status()
    obj = r.json()
    #print(obj)
    print("confirmation number:%s"%(obj.get("confirmations",None)))
    operations = obj.get("operations", None)
    confirmation=obj.get("confirmations",None)
    if not confirmation or int(confirmation)<1:
        labelb = tkinter.Label(win, text="操作次数：%d,确认数:%d/1, 网络尚未确认该交易，请稍后重新点击确认按钮:"%(counter,int(confirmation)))
        labelb.pack()
    elif operations==None:
        labelb = tkinter.Label(win, text="操作次数：%d,网络尚未确认该交易，请稍后重新点击确认按钮:"%(counter))
        labelb.pack()
    else:
        success=False
        if operations:
            for operation in operations:
                token_data = operation["tokenInfo"]
                if token_data["address"]==token_address:
                    print(operation.keys())
                    address=operation["to"]
                    print("address:%s"%address)
                    value = float(operation["value"])
                    value = value / (10 ** 18)
                    if recv_address in [address]:
                        print("value")
                        str_value = "%.6f" % value
                        str_amount = "%.6f" % amount
                        if str_value==str_amount:
                            print("check success")
                            success= True
                            break
                        else:
                            labelb = tkinter.Label(win, text="操作次数：%d，金额错误请按照正确金额重新转账:"%counter)
                            labelb.pack()
            labelc = tkinter.Label(win, text="操作次数：%d,无匹配交易，请重新输入您的交易哈希:"%(counter))
            labelc.pack()
        if success:
            #win.destroy()
            signature = b64encode(rsa.sign(new_msg.encode(), private, "SHA-1"))
            check_and_save(signature)

def get_transaction():
    global win,tran,button
    label = tkinter.Label(win, text="请输入交易哈希（Transaction Hash）:")
    label.pack()
    tran = tkinter.Entry(win, width=50, bg="white", fg="black")
    tran.pack()
    button.destroy()
    button = tkinter.Button(win, text="确定", command=check_status)  # 收到消息执行这个函数
    button.pack()  # 加载到窗体，

def init_sell(apikey,apisecret,total_load_coin,load_money,trade_type):
    access_key = apikey.strip()
    access_secret = apisecret.strip()
    _money =load_money.strip().lower()
    tmp =total_load_coin.strip().lower()
    if " "in tmp:
        coins =tmp.split(" ")
    else:
        coins = [tmp]
    markets = [_coin+_money for _coin in coins]
    print(markets)
    partition = int(load_parition.strip())
    assert(partition!=0)
    api = fcoin_api(access_key, access_secret)
    min_size=api.set_demical(_money, coins)
    for market in markets:
        print("cancel"+market)
        api.cancel_all_pending_order(market,trade_type)
        time.sleep(0.5)
    for _coin in coins:
        market=_coin+_money
        obj = api.get_depth(market)
        buy13 = obj["bids"][12 * 2]
        money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin,trade_type)
        if coin>min_size[market]:
            api.take_order(market, "sell", buy13, coin, coin_place,trade_type)
            time.sleep(0.5)

if __name__ == '__main__':
    multiprocessing.freeze_support()

    print("begin")

    load_access_key, load_access_secret, load_money, load_coin, load_parition, load_total_money, load_bidirection, load_coin_place = None, None, None, None, None, None, None, None
    win1 = None
    license_day=0
    emerency = False

    mutex1 = threading.Lock()
    mutex3 = threading.Lock()
    mutex4 = threading.Lock()
    mutex5 = threading.Lock()

    access_key = None
    access_secret = None

    _money =None
    coins = None
    min_size = None
    money_have = None

    api = None
    partition=0
    bidirection=3
    coin_place = "main"
    total_amount_limit = 0
    yanzheng_file_name = "C:\guadan_yanzheng.txt"
    gap = "guadan"
    config_file = "guadan_coinlastconfig.txt"
    multi_config_file = "multi_account_config.txt"

    need_exit = False
    coins = list()
    coin_place_list = list()
    markets = list()


    load_money = "usdt"
    total_load_coin="ltc eos btc eth xrp bch etc xlm zec ada dash trx"
    load_coin = "ltc"
    load_parition="2"
    load_bidirection="3"
    load_coin_place="1"
    processes =list()
    first_time=True
    while True:
        with open(multi_config_file, "r") as f:
            for line in f.readlines():
                apikey = line.split("#")[0]
                apisecret = line.split("#")[1]
                total_money = line.split("#")[2]
                load_money=line.split("#")[3]
                load_coin=line.split("#")[4]
                account_type=line.split("#")[5].strip()
                if first_time:
                    first_time=False
                    try:
                        #init_sell(apikey,apisecret,total_load_coin,load_money,account_type)
                        pass
                    except:
                        pass

                p1 = Process(target=tick, args=(
                    apikey, apisecret, load_money, load_coin, load_parition, total_money,
                    load_bidirection, load_coin_place,account_type))
                p1.daemon = True
                p1.start()
                processes.append(p1)
        processes[0].join(timeout=10800)
        for p in processes:
            p.terminate()
        processes=[]

  #  period_restart()









