import falcon
import json
import ccxt
import yaml
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys as keys
from requests import Session

def fetch(url, method='GET', headers=None, body=None):
    session = Session()
    response = session.request(
        method,
        url,
        data=body,
        timeout=2000
    )
    return response


def bitmex(driver):

    url = "https://www.bitmex.com/api/v1/instrument/activeAndIndices"
    #res = fetch(url)
    #print(res)
    
    sell_id = "sellVolumePerMeasurementTime"
    buy_id = "buyVolumePerMeasurementTime"

    with open("setting.yaml", "r+") as f:
        data = yaml.load(f)

    bitmex = ccxt.bitmex({
        'apiKey': data["bitmex"]["id"],
        'secret': data["bitmex"]["sec"],
        "timeout":200000
    })
    #print(bitmex.fetch_ticker('BTC/USD'))
    try:
        #bitmex.create_order('BTC/USD', type='market', side='buy', amount=100)
        #print(bitmex.fetch_ticker('BTC/USD'))
        print("start")
    except:
        print("errorr rrrrrrrr")
        return

    position = "NONE" # NONE, BUY, SELL 
    pos_price = 0
    cnt = 0
    f1 = open("mex_log.csv", "a")
    f2 = open("mex_trade.csv", "a")
    pre_diff = None
    while(True):

        '''
        try:
            now = time.time()
            last = bitmex.fetch_ticker('BTC/USD')['last']
            f.write("{},{}\n".format(now,last))
            print(now,last)
        except:
            print("error occured!")
        time.sleep(5)
        continue
        '''

        try:
            price = bitmex.fetch_ticker('BTC/USD')['last']
        except:
            print("wait... //70")
            time.sleep(5)
            continue

        cnt += 1
        if cnt % 100 == 0:
            usd = bitmex.private_get_position()[0]['currentQty']
            print(usd)

        sell_volume = float(driver.find_element_by_id(sell_id).text)
        buy_volume = float(driver.find_element_by_id(buy_id).text)

        if pre_diff is None:
            pre_diff = sell_volume - buy_volume
            time.sleep(5)
            continue

        now = time.time()
        f1.write("{},{},{},{},{},{}\n".format(now, sell_volume, buy_volume, pre_diff, position,price))

        diff = buy_volume - sell_volume

        diff_delta = diff - pre_diff

        print(sell_volume, buy_volume, int(diff_delta), position, price)

        # ドテン買い
        if diff_delta > 50:

            # 買いポジションじゃなければドテン
            if position == "NONE":
                print("bitmex_buy 100")
                pos_price = price
                f2.write("{},{},{}\n".format(now,price,"BUY"))
                bitmex_buy(bitmex, 100)
            elif position == "SELL":
                print("bitmex_buy 200")
                pos_price = price
                f2.write("{},{},{}\n".format(now,price,"BUY"))
                bitmex_buy(bitmex, 200)

            position = "BUY"
            

        # ドテン売り
        elif diff_delta < -50:

            # 売りポジションじゃなければドテン
            if position == "NONE":
                print("bitmex_sell 100")
                pos_price = price
                f2.write("{},{},{}\n".format(now,price,"SELL"))
                bitmex_sell(bitmex, 100)
            elif position == "BUY":
                print("bitmex_sell 200")
                pos_price = price
                f2.write("{},{},{}\n".format(now,price,"SELL"))
                bitmex_sell(bitmex, 200)

            position = "SELL"
            

        # 損切り判定
        else:
            if position == "BUY":
                if price / pos_price  < 0.95:
                    print("bitmex_sell lc 100")
                    position = "NONE"
                    pos_price = 0
                    bitmex_sell(bitmex, 100)
                    f2.write("{},{},{}\n".format(now,price,"SELL"))


            elif position == "SELL":
                if price / pos_price > 1.05:
                    print("bitmex_buy lc 100")
                    position = "NONE"
                    pos_price = 0
                    bitmex_buy(bitmex, 100)
                    f2.write("{},{},{}\n".format(now,price,"BUY"))

        pre_diff = diff
        time.sleep(4)




def bitmex_buy(bitmex, amount, price=None):

    while True:
        try:
            if price is None:
                order = bitmex.create_order('BTC/USD', type='market', side='buy', amount=amount)
                break
            else:
                order = bitmex.create_order('BTC/USD', type='limit', side='buy', amount=amount, price=price)
                break
        except:
            print("retry buy")
            time.sleep(3)

            
    return order
    

def bitmex_sell(bitmex, amount, price=None):

    while True:
        try:
            if price is None:
                order = bitmex.create_order('BTC/USD', type='market', side='sell', amount=amount)
                break
            else:
                order = bitmex.create_order('BTC/USD', type='limit', side='sell', amount=amount, price=price)
                break
        except:
            print("retry sell")
            time.sleep(3)     
    return order


def create_driver():
    
    driver = webdriver.PhantomJS('G:/ダウンロード/line-entry/phantomjs-2.1.1-windows/bin/phantomjs.exe')
    driver.implicitly_wait(10)
    url = "https://inagoflyer.appspot.com/btcmac"
    driver.get(url)
    
    time.sleep(5)
    checkbox = driver.find_elements_by_css_selector("#chart_table_tbody input[type='checkbox']")
    for cb in checkbox:
        print(cb.get_attribute("id"))
        if cb.get_attribute("id") == "BitMEX_BTCUSD_checkbox":
            continue
        cb.click()

    return driver


if __name__ == "__main__":

    driver = create_driver()
    bitmex(driver)

