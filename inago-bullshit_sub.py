import falcon
import json

import ccxt
import yaml

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys as keys

import time
from datetime import datetime

def log_volume():
    driver = webdriver.PhantomJS('G:/ダウンロード/line-entry/phantomjs-2.1.1-windows/bin/phantomjs.exe')
    driver.implicitly_wait(10)
    url = "https://inagoflyer.appspot.com/btcmac"
    driver.get(url)

    sell_id = "sellVolumePerMeasurementTime"
    buy_id = "buyVolumePerMeasurementTime"


    f = open("inago.csv", "w")

    while(True):
        now = time.time()
        #now = datetime.fromtimestamp(now)
        sell_volume = float(driver.find_element_by_id(sell_id).text)
        buy_volume = float(driver.find_element_by_id(buy_id).text)
        print(sell_volume, buy_volume)
        f.write("{},{},{}\n".format(now,sell_volume,buy_volume))
        time.sleep(1)

    driver.quit()
    return 

if __name__ == "__main__":
    log_volume()
