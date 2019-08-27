import rsa
from base64 import b64encode, b64decode
import os
import uuid
from manbi import *
import threading
import base64
from multiprocessing import Process
import multiprocessing
import time

'''
采用AES对称加密算法
'''


# str不是16的倍数那就补足为16的倍数
def add_to_16(value):
    while len(value) % 16 != 0:
        value += '\0'
    return str.encode(value)  # 返回bytes


# 加密方法
def encrypt_oracle(text):
    # 秘钥
    key = 'fhkgg'
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    # 先进行aes加密
    encrypt_aes = aes.encrypt(add_to_16(text))
    # 用base64转成字符串形式
    encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
    return (encrypted_text)


# 解密方法
def decrypt_oralce(text):
    # 秘钥
    key = 'fhkgg'
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    # 优先逆向解密base64成bytes
    base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))
    # 执行解密密并转码返回str
    decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '')
    return (decrypted_text)


class Section:
    # 粘贴的回调函数
    def onPaste(self):
        try:
            self.text = win.clipboard_get()
            # 获得系统粘贴板内容
        except tkinter.TclError:
            pass
        # 防止因为粘贴板没有内容报错
        show.set(str(self.text))
        # 在文本框中设置刚刚获得的内容

    def onPaste1(self):
        try:
            self.text = win.clipboard_get()
            # 获得系统粘贴板内容
        except tkinter.TclError:
            pass
        # 防止因为粘贴板没有内容报错
        show1.set(str(self.text))
        # 在文本框中设置刚刚获得的内容

    def onPaste2(self):
        try:
            self.text = win.clipboard_get()
            # 获得系统粘贴板内容
        except tkinter.TclError:
            pass
        # 防止因为粘贴板没有内容报错
        show2.set(str(self.text))
        # 在文本框中设置刚刚获得的内容

    # 复制的回调函数
    def onCopy(self):
        self.text = T.get(1.0, tkinter.END)
        # 获得文本框内容
        win.clipboard_append(self.text)
        # 添加至系统粘贴板


def get_mac_address():
    node = uuid.getnode()
    mac = uuid.UUID(int = node).hex[-12:]
    # return mac
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = encrypt_oracle(s.getsockname()[0]).strip()
    ret = mac+"***"+ip
    return ret


def check_and_save():
    signature = entry1.get().strip().encode()
    new_msg = msg1 + gap + "bitchoice"
    try:
        rsa.verify(new_msg.encode(), b64decode(signature), public)
    except:
        print("wrong license!!!")
        a = input("")
        sys.exit()
    with open(yanzheng_file_name, 'w') as f:
        f.write(encrypt_oracle(msg1 + ":::::" + signature.decode()))

    win.destroy()


def buy_main_body(mutex2, api, expire_time, bidirection, partition, _money, _coin, min_size,
                  money_have, leverage):
    def paixu(mutex2, api, expire_time, bidirection, partition, _money, _coin, min_size,
                  money_have, leverage):

        market = _coin + _money
        market = market.upper()
        min_price_tick =api.price_decimal[market]
        _start_time = time.time()
        while True:
            try:
                api.cancel_all_pending_order(market)

                time.sleep(1)
                money, coin, short_coin = api.get_available_balance(market)
                step_coin = (coin / 2)
                step_money = min(money_have, money) / 2
                print("step_coin:",step_coin)
                print("step_money:",step_money)
                buy1, buy1_amount, ask1, ask1_amount, average = api.get_buy1_and_ask1(market)
                sell_price1 = ask1 + 3 * min_price_tick
                sell_price1 = api.price_format(sell_price1, api.price_decimal[market], 1)
                buy_price1 = buy1 - 3 * min_price_tick
                buy_price1 = api.price_format(buy_price1, api.price_decimal[market], 1)

                if step_coin >= min_size:
                    api.take_order(market, "sell", sell_price1, step_coin, leverage)
                amount_can_buy =  api.amount_can_buy(market,leverage,step_money,buy_price1)
                if amount_can_buy >= min_size:
                    api.take_order(market, "buy", buy_price1, amount_can_buy,leverage)

                sell_price2 = ask1 + 9 * min_price_tick
                sell_price2 = api.price_format(sell_price2, api.price_decimal[market], 1)
                buy_price2 = buy1 - 9 * min_price_tick
                buy_price2 = api.price_format(buy_price2, api.price_decimal[market], 1)

                if step_coin >= min_size:
                    api.take_order(market, "sell", sell_price2, step_coin, leverage)
                amount_can_buy = api.amount_can_buy(market,leverage,step_money,buy_price2)
                if amount_can_buy >= min_size:
                    api.take_order(market, "buy", buy_price2, amount_can_buy,leverage)
                while True:
                    time.sleep(1)
                    buy1, buy1_amount, ask1, ask1_amount, average = api.get_buy1_and_ask1(market)
                    ask_upper1 = ask1 + 4 * min_price_tick
                    ask_lower1 = ask1 + 1 * min_price_tick
                    buy_lower1 = buy1 - 4 * min_price_tick
                    buy_upper1 = buy1 - 1 * min_price_tick
                    ask_upper2 = ask1 + 14 * min_price_tick
                    ask_lower2 = ask1 + 5 * min_price_tick
                    buy_lower2 = buy1 - 14 * min_price_tick
                    buy_upper2 = buy1 - 5 * min_price_tick

                    print("ask1:",sell_price1)
                    print("buy1:",buy_price1)
                    print("ask_lower1:",ask_lower1)
                    print("buy_upper1:",buy_upper1)
                    if sell_price1 <= ask_lower1 or sell_price2 > ask_upper2 or buy_price1 > buy_upper1 or buy_price2 < buy_lower2:
                        break
            except Exception as err:
                print(err)

    def guadan(mutex2, api, expire_time, bidirection, partition, _money, _coin, min_size,
                  money_have, leverage):
        market = _coin + _money
        market = market.upper()
        min_price_tick =api.price_decimal[market]
        ratios1 = [0.005,0.006,0.007,0.008,0.009]
        while True:
            try:
                buy1, buy1_amount, ask1, ask1_amount, average = api.get_buy1_and_ask1(market)
                last_buy_level_1 = buy1 - buy1 * ratios1[0]
                last_sell_level_1 = ask1 + ask1 * ratios1[0]
                api.cancel_all_pending_order(market)
                money, coin,short_coin = api.get_available_balance(market)
                available_coin = coin
                available_money = min(money, money_have)
                coin_for_each_trade = int(available_coin / len(ratios1))
                money_for_each_trade = available_money / len(ratios1)

                for i, ratio in enumerate(ratios1):
                    buy_price = buy1 - buy1 * ratio
                    time.sleep(0.05)
                    amount_can_buy = api.amount_can_buy(market, leverage, money_for_each_trade, buy_price)
                    buy_amount = max(min_size, amount_can_buy)
                    api.take_order(market, "buy", buy_price, buy_amount,leverage)

                sell_amount = (max(coin_for_each_trade, min_size))
                for i, ratio in enumerate(ratios1):
                    sell_price = ask1 + ask1 * ratio
                    time.sleep(0.05)
                    api.take_order(market, "sell", sell_price, sell_amount, leverage)

                while True:
                    time.sleep(1)
                    buy1, buy1_amount, ask1, ask1_amount, average = api.get_buy1_and_ask1(market)
                    print("trade_pair:",market,"buy:",buy1)
                    buy_bound = buy1-buy1*0.004
                    sell_bound = ask1+ask1*0.004
                    if last_buy_level_1>buy_bound or last_sell_level_1<sell_bound:
                        break

            except Exception as err:
                print(err)

    def jiaoyi(mutex2, api, expire_time, bidirection, partition, _money, _coin, min_size,
                  money_have, leverage):
        market = _coin+_money
        direction = "buy"
        min_price_tick = 1 / (10 ** api.price_decimal[market])
        first_time=True
        ratio_list = list()

        while True:
            try:
                begin_time=time.time()
                api.cancel_all_pending_order(market)
                money, coin, short_coin= api.get_available_balance(market)
                buy1, buy1_amount, ask1, ask1_amount, average = api.get_buy1_and_ask1(market)
                mining_price = ask1 if ask1_amount<buy1_amount else buy1
                if first_time:
                    init_money = api.get_total_balance()
                    money_loss = init_money*0.5
                    first_time=False
                current_money = api.get_total_balance()
                loss = init_money-current_money
                print("trade_pair:",market,"loss:",loss)
                if loss>money_loss:

                    if coin>min_size:
                        api.take_order(market, "sell", ask1 *0.97, coin, leverage)
                    if short_coin>min_size:
                        api.take_order(market, "closeshort", buy1 *1.03, short_coin, leverage)
                else:
                    counter = 0
                    need_cancel= True
                    while True:
                        print("average:",average)
                        print("counter:",counter)
                        if time.time()-begin_time>60:
                            break
                        elif counter>=average:
                            time.sleep(1)
                        else:
                            id1=id2=id3=id4="-1"
                            buy1, buy1_amount, ask1, ask1_amount, average = api.get_buy1_and_ask1(market)
                            money, coin, short_coin = api.get_available_balance(market)
                            if coin>min_size:
                                id1=api.take_order(market, "sell", mining_price, coin, leverage)
                            if short_coin>min_size:
                                id2=api.take_order(market, "closeshort", mining_price, short_coin, leverage)
                            money, coin, short_coin = api.get_available_balance(market)
                            amount_can_buy = api.amount_can_buy(market, leverage, money/2, mining_price)
                            if amount_can_buy>min_size:
                                id3 =api.take_order(market, "buy", mining_price, amount_can_buy, leverage)
                                id4 =api.take_order(market, "openshort", mining_price, amount_can_buy, leverage)
                            if id1!="-1":
                                counter+=api.get_filled_amount(market,id1)
                            if id2!="-1":
                                counter+=api.get_filled_amount(market,id2)
                            if id3!="-1":
                                counter+=api.get_filled_amount(market,id3)
                            if id4!="-1":
                                counter+=api.get_filled_amount(market,id4)

            except Exception as ex:
                print(sys.stderr, 'error: ', ex)
                pass

    jiaoyi(mutex2, api, expire_time, bidirection, partition, _money, _coin, min_size,
          money_have, leverage)

def load_record():
    global load_access_key, load_access_secret, load_money, load_coin, load_parition, load_total_money, load_bidirection, load_coin_place
    with open(config_file, 'r') as f:
        tmp = f.read()
        tmp = decrypt_oralce(tmp)
      #  print(tmp)
        parameters = tmp.split(gap)
        load_access_key = parameters[0]
        load_access_secret = parameters[1]
        load_money = parameters[2]
        load_coin = parameters[3]
        load_parition = parameters[4]
        load_total_money = parameters[5]
        load_bidirection = parameters[6]
        load_coin_place = parameters[7]


def tick(load_access_key, load_access_secret, load_money, load_coin, load_parition, load_total_money, load_bidirection,
         load_coin_place, expire_time="0"):
    try:



        mutex2 = threading.Lock()
        access_key = load_access_key.strip()
        access_secret = load_access_secret.strip()
        _money = load_money.strip().upper()
        tmp = load_coin.strip().upper()
        if " " in tmp:
            coins = tmp.split(" ")
        else:
            coins = [tmp]
        markets = [_coin + _money for _coin in coins]
        print(markets)
        partition = int(load_parition.strip())
        assert (partition != 0)
        money_have = float(load_total_money.strip())
        #money_have = min(400, money_have)

        market_exchange_dict = {"bbgcusdt": "renren", "btmusdt": "jingxuanremenbi", "zipusdt": "servicex",
                                "fiusdt": "fiofficial", "dogeusdt": "tudamu", "aeusdt": "servicex", "zrxusdt": "tudamu",
                                "batusdt": "jiucai", "linkusdt": "jingxuanremenbi", "icxusdt": "allin",
                                "omgusdt": "ninthzone", "zilusdt": "langchao"}

        bidirection = int(load_bidirection.strip())
        coin_place = load_coin_place.strip()

        api = fcoin_api(access_key, access_secret)
        min_size = api.set_demical()
        print("start cancel existing pending orders")
        for market in markets:
            time.sleep(0.1)
            api.cancel_all_pending_order(market)
        print("cancel pending orders completed")
        for i, market in enumerate(markets):
            time.sleep(0.1)
            try:
                init_sell(api,_money,coins[i],coin_place)
            except:
                pass
            thread = threading.Thread(target=buy_main_body, args=(
            mutex2, api, expire_time, bidirection, partition, _money, coins[i],
            min_size[market], money_have / len(markets), coin_place))
            thread.setDaemon(True)
            thread.start()
        time.sleep(3600)
        print("tick exit!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    except Exception as ex:
        print(sys.stderr, 'tick: ', ex)
        # a= input()


def cancel_exit():
    global global_process, load_access_key, load_access_secret, load_money, load_coin, heart_T, win
    access_key = load_access_key.strip()
    access_secret = load_access_secret.strip()
    _money = load_money.strip().upper()
    tmp = load_coin.strip().upper()
    if " " in tmp:
        coins = tmp.split(" ")
    else:
        coins = [tmp]
    markets = [_coin + _money for _coin in coins]
    print(markets)
    partition = int(load_parition.strip())
    assert (partition != 0)
    api = fcoin_api(access_key, access_secret)
    global_process.terminate()
    heart_T.insert(tkinter.END, "正在撤单,请稍后\n")
    win.update()
    for market in markets:
        time.sleep(0.1)
        api.cancel_all_pending_order(market)
    heart_T.insert(tkinter.END, "撤单结束,安全退出\n")
    win.update()
    time.sleep(1)
    sys.exit()


heart_T = None
global_process = None
heart_counter = None


def real_save_record():
    global heart_counter, global_process, heart_T, win, global_config, load_access_key, load_access_secret, load_money, load_coin, load_parition, load_total_money, load_bidirection, load_coin_place, label1, label2, label4, label5, label6, label7, label8, label9, button, run_label, hert_label

    load_access_key = save_access_key = entry1.get().strip()
    load_access_secret = save_access_secret = entry2.get().strip()
    load_money = save__money = entry4.get().strip().upper()
    load_coin = save__coin = entry5.get().strip().upper()
    load_parition = save_parition = entry6.get().strip()
    load_total_money = save_total_money = (entry7.get().strip())
    load_bidirection = save_bidirection = (entry8.get().strip())
    load_coin_place = save_coin_place = (entry9.get().strip())

    tmp = save_access_key + gap + save_access_secret + gap + save__money + gap + save__coin + gap + save_parition + gap + save_total_money + gap + save_bidirection + gap + save_coin_place
    global_config = encrypt_oracle(tmp)

    with open(config_file, 'w') as f:
        f.write(global_config)
    win.destroy()





def save_record():
    real_save_record()


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
    # license_day  = 0.00069
    win.destroy()


# 导入密钥
labela = None
labelb = None
labelc = None
counter = 0


def check_status():
    global win, tran_id, tran, msg1, gap, button, recv_address, amount, labela, labelc, labelb, counter
    token_address = "0x7dd8d8f4ef294cd417d17a9ea6c4a0fb146d90b5"
    counter += 1
    if labela:
        labela.destroy()
        labela = None
    if labelb:
        labelb.destroy()
        labelb = None
    if labelc:
        labelc.destroy()
        labelc = None
    labela = tkinter.Label(win, text="操作次数：%d,请等待网络确认:" % (counter))
    labela.pack()
    new_msg = msg1 + gap + "bitchoice"
    tran_id = tran.get().strip()
    URL = "http://api.ethplorer.io/getTxInfo/" + tran_id + "?apiKey=freekey"
    print("tran_id:%s" % tran_id)
    _continue = True
    obj = dict()
    try:
        r = requests.request("GET", URL, timeout=10)
        r.raise_for_status()
        obj = r.json()
    except:
        pass
    # print(obj)
    print("confirmation number:%s" % (obj.get("confirmations", None)))
    operations = obj.get("operations", None)
    confirmation = obj.get("confirmations", None)
    if "error" in obj.keys():
        if "format" in obj["error"]["message"]:
            labelb = tkinter.Label(win, text="操作次数：%d, 交易哈希格式错误,请重新输入再点击确认按钮:" % (counter))
            labelb.pack()
        else:
            labelb = tkinter.Label(win, text="操作次数：%d,网络尚未确认该交易，请稍后重新点击确认按钮:" % (counter))
            labelb.pack()
    elif int(confirmation) < 1:
        labelb = tkinter.Label(win, text="操作次数：%d,确认数:%d/1, 网络尚未确认该交易，请稍后重新点击确认按钮:" % (counter, int(confirmation)))
        labelb.pack()
    elif operations == None:
        labelb = tkinter.Label(win, text="操作次数：%d,网络尚未确认该交易，请稍后重新点击确认按钮:" % (counter))
        labelb.pack()
    else:
        success = False
        if operations:
            for operation in operations:
                token_data = operation["tokenInfo"]
                if token_data["address"] == token_address:
                    print(operation.keys())
                    address = operation["to"]
                    print("address:%s" % address)
                    value = float(operation["value"])
                    value = value / (10 ** 18)
                    if recv_address in [address]:
                        print("value")
                        str_value = "%.6f" % value
                        str_amount = "%.6f" % amount
                        if str_value == str_amount:
                            print("check success")
                            success = True
                            break
                        else:
                            labelb = tkinter.Label(win, text="操作次数：%d，金额错误请按照正确金额重新转账:" % counter)
                            labelb.pack()
            labelc = tkinter.Label(win, text="操作次数：%d,无匹配交易，请重新输入您的交易哈希:" % (counter))
            labelc.pack()
        if success:
            # win.destroy()
            signature = b64encode(rsa.sign(new_msg.encode(), private, "SHA-1"))
            check_and_save(signature)


def get_transaction():
    global win, tran, button
    label = tkinter.Label(win, text="请输入交易哈希（Transaction Hash）:")
    label.pack()
    tran = tkinter.Entry(win, width=50, bg="white", fg="black")
    tran.pack()
    button.destroy()
    button = tkinter.Button(win, text="确定", command=check_status)  # 收到消息执行这个函数
    button.pack()  # 加载到窗体，




def init_sell(api,_money,_coin,coin_place):
    market = _coin+_money
    buy1, ask1,average = api.get_buy1_and_ask1(market)
    money, coin, short_coin = api.get_available_balance(market)
    if coin>min_size[market]:
        api.take_order(market, "sell", buy1*0.99, coin, coin_place)
        time.sleep(0.5)
def get_register_code():
    global win,registerentry,register_code,expired_time
    register_code=registerentry.get().strip()
    r = requests.request("GET","http://47.88.86.168/self_team/manbi/register.php?&code=" + register_code)
    if r.status_code == 200:
        obj = r.json()
    else:
        print("connect error!")
        return
    if obj["status"] == "OK":
        expired_time = float(obj["expire_time"])
        win.destroy()
    else:
        print("register code error!")
        return


if __name__ == '__main__':
    multiprocessing.freeze_support()

    print("begin")

    load_access_key, load_access_secret, load_money, load_coin, load_parition, load_total_money, load_bidirection, load_coin_place = None, None, None, None, None, None, None, None
    win1 = None
    license_day = 0
    emerency = False

    mutex1 = threading.Lock()
    mutex3 = threading.Lock()
    mutex4 = threading.Lock()
    mutex5 = threading.Lock()

    access_key = None
    access_secret = None

    _money = None
    coins = None
    min_size = None
    money_have = None

    api = None
    partition = 0
    bidirection = 3
    coin_place = "2"
    total_amount_limit = 0
    yanzheng_file_name = "C:\manbi_vip.txt"
    gap = "manbi"
    config_file = "manbi_lastconfig.txt"
    multi_config_file = "multi_account_config.txt"

    need_exit = False
    coins = list()
    coin_place_list = list()
    markets = list()

    load_money = "USDT"
    total_load_coin="BTC LTC ETH EOS"
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
                load_leverage=line.split("#")[5].strip()
                if first_time:
                    first_time=False
                    try:
                        #init_sell(apikey,apisecret,total_load_coin,load_money,account_type)
                        pass
                    except:
                        pass

                p1 = Process(target=tick, args=(
                    apikey, apisecret, load_money, load_coin, load_parition, total_money,
                    load_bidirection, load_leverage))
                p1.daemon = True
                p1.start()
                processes.append(p1)
        processes[0].join(timeout=3600*24)
        for p in processes:
            p.terminate()
        processes=[]







