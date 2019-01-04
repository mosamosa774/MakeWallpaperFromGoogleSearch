from datetime import datetime
import urllib.parse
import requests
from bs4 import BeautifulSoup
import base64
import os
import time
import chromedriver_binary
import cv2
from selenium import webdriver
import re
import subprocess

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)  # 今は chrome_options= ではなく options=

url = "https://www.google.co.jp/search?q={0}&tbm=isch"


def getSearchedImages(_max, word):
    _url = url.format(urllib.parse.quote(word))
    driver.get(_url)
    print('wait')
    tmp_max = _max
    if (tmp_max > 20):
        tmp_max += 20
        tmp_max -= tmp_max % 20
    for __ in range(int(tmp_max/20)-1):  # 1*20
        driver.execute_script("window.scrollBy(0, 500000)")
        time.sleep(1)
    time.sleep(3*(int(tmp_max/20)-1))
    # res = requests.get(_url)
    # res.encoding = res.apparent_encoding
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    # print(page_source.replace("\xa0","").replace("\u2013",""))
    img_list = {'base64': [], 'http': []}
    count = 0
    error_count = 0
    divs = soup.find_all("div")
    for div in divs:
        try:
            if (div.attrs['jscontroller'] == 'Q7Rsec'):
                src = div.find("img").attrs['src']
                if (re.match("https://", src)):
                    img_list['http'].append(src)
                else:
                    img_list['base64'].append(src.split(',')[1])
                count += 1
                if (_max < count):
                    break
        except:
            error_count += 1
            pass
    print(count, error_count, len(img_list['http']), len(img_list['base64']))
    return img_list


def translateBase64_2_Img(img_list):
    now = datetime.now()
    dist = "output_"+str(now).replace(":", " ").split(".")[0].replace(" ", "_")
    count = 0
    os.makedirs(dist)
    for i in img_list['base64']:
        with open(dist+"/img" + str(count) + ".jpg", "wb") as fh:
            print('dealing...', count)
            fh.write(base64.b64decode(i))
            count += 1

    for i in img_list['http']:
        print('dealing...', count)
        command = "curl "+i+" > " + dist + "/img" + str(count) + ".jpg"
        count += 1
        proc = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        proc.communicate()
        time.sleep(1)

    imgs = []
    print("start create")
    for i in range(count):
        print("read: ", dist+'/img' + str(i) + '.jpg')
        imgs.append(cv2.imread(dist+'/img' + str(i) + '.jpg'))
    return imgs
