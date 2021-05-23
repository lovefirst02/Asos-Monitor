#coding=utf-8
import requests
import json
import time
import datetime
from bs4 import BeautifulSoup as soup
from multiprocessing import Process
from discord_webhook import DiscordEmbed, DiscordWebhook
import random
from imgurpython import ImgurClient
from threading import Thread
from colorama import init
import twder
import re

init(autoreset=True)

class FileNotFound(Exception):
    ''' Raised when a file required for the program to operate is missing. '''

class NoDataLoaded(Exception):
    ''' Raised when the file is empty. '''

class frontcolor():
    def green(text):
        text = "\033[0;32;40m{}\33[0m".format(text)
        return text

    def red(text):
        text = "\033[0;31;40m{}\33[0m".format(text)
        return text

    def yellow(text):
        text = "\033[0;33;40m{}\33[0m".format(text)
        return text

    def sky(text):
        text = "\033[0;36;40m{}\33[0m".format(text)
        return text

def dollar(p,dol):
    if dol == 'TWD':
        return
    price = re.findall(r'[0-9]\d*.\d*.\d*[0-9]\d*',p)[0]
    a = twder.now(dol)[3]
    b = float(price.replace(',','.')) * float(a)
    print(round(b,2))
    #c = "TWD：{}".format(round(b,2))
    return str(round(b,2))

def read_from_txt(path):
    raw_lines = []
    lines = []
    try:
        f = open(path, 'r')
        raw_lines = f.readlines()
        f.close()
    except:
        raise FileNotFound()

    if(len(raw_lines) == 0):
        raise NoDataLoaded()

    for line in raw_lines:
        lines.append(line.strip("\n"))

    return lines


def connectasos(url):
    #headers = {'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'}
    url1 = (url)
    #condition = True
    #while condition == True:
    try:
        r = requests.get(url1)
        products = json.loads((r.text))['products']
        print(frontcolor.yellow("獲取原始資料成功 ----- " + url))
    except:
        print (frontcolor.red("獲取原始資料失敗，睡眠3分鐘"))
        time.sleep(180)

    return products

def currentp(url):
    products = connectasos(url)
    current_product = []
    for product in products:
        products = (product['name'])
        current_product.append(products)

    #print("Successfully currentp")

    return current_product

def message_post(webhook_url,name,link,imageaddress,price,currency,brand):
    now = datetime.datetime.now()
    try:
        webhook = DiscordWebhook(url=webhook_url, content='')
        embed = DiscordEmbed(title=name, color=random.randint(0, 16777215), url=link)
        #embed.add_embed_field(name='**產品名稱：**',value= name)
        embed.add_embed_field(name='**品牌：**', value=brand)
        embed.add_embed_field(name='**售價：**', value=price + '\n' + '幣別：' + currency)
        embed.set_thumbnail(imageaddress)
        embed.set_footer(text='ASOS Monitor By Wang')
        embed.set_timestamp()
        webhook.add_embed(embed)
        webhook.execute()
        print(frontcolor.green(str(now) + '[SUCCESS] --> 成功傳送WebHook'))
    except:
        print(frontcolor.red(str(now) + '[ERROR] --> WebHook傳送失敗'))
        pass

def newp(url):
    client_id = 'Imgur_client_id'
    client_secret = 'Imgur_client_secret'
    client = ImgurClient(client_id, client_secret)
    album = None
    config = {
        '#album': album
    }
    if url == 'https://www.asos.com/api/product/search/v2/categories/27110?channel=desktop-web&country=TW&currency=TWD&keyStoreDataversion=jqvkhhb-21&lang=en&limit=72&offset=0&rowlength=4&store=ROW':
        domain = 'https://www.asos.com/'
    elif url == 'https://www.asos.com/api/product/search/v2/categories/27110?channel=desktop-web&country=US&currency=USD&keyStoreDataversion=jqvkhhb-21&lang=en&limit=72&offset=0&rowlength=4&store=US':
        domain = 'https://www.asos.com/us/'
    elif url == 'https://www.asos.com/api/product/search/v2/categories/27110?channel=desktop-web&country=GB&currency=GBP&keyStoreDataversion=jqvkhhb-21&lang=en&limit=72&offset=0&rowlength=4&store=COM':
        domain = 'https://www.asos.com/'
    elif url == 'https://www.asos.fr/api/product/search/v2/categories/27110?channel=desktop-web&country=WF&currency=GBP&keyStoreDataversion=jqvkhhb-21&lang=fr&limit=72&offset=0&rowlength=4&store=FR':
        domain = 'https://www.asos.fr/'
    elif url == 'https://www.asos.com/api/product/search/v2/categories/27110?channel=desktop-web&country=VI&currency=GBP&keyStoreDataversion=jqvkhhb-21&lang=en&limit=72&offset=0&rowlength=4&store=US':
        domain = 'https://www.asos.com/us/'
    elif url == 'https://www.asos.com/api/product/search/v2/categories/27110?channel=desktop-web&country=CX&currency=GBP&keyStoreDataversion=jqvkhhb-21&lang=en&limit=72&offset=0&rowlength=4&store=AU':
        domain = 'https://www.asos.com/au/'
    else:
        domain = 'https://www.asos.com/'
    paget = 0
    current_products = currentp(url)
    while True:
        if paget >= 0:
            try:
                r = requests.get(url)
                products = json.loads((r.text))['products']
                time.sleep(5)
                now = datetime.datetime.now()
                print(frontcolor.green(str(now) + " -- 獲取 -- " + "asos " + url))
            except:
                print(frontcolor.red("IP禁止 -- 睡眠3分鐘"))
                time.sleep(180)

            new_products = []
            for product in products:
                products1 = (product['name'])
                new_products.append(products1)

            if new_products != current_products:
                new_prod = list(set(new_products) - set(current_products))
                for x in range(len(new_prod)):
                    current_products.insert(x, new_prod[x])

                    name = products[x]['name']
                    urllink = products[x]['url']
                    link = (domain+urllink)



                    image = products[x]['imageUrl']
                    imageaddress = ("https://{}".format(image))
                    try:
                        r = requests.get(imageaddress)
                        with open(r"test.jpg", 'wb') as photo:
                            photo.write(r.content)
                            image = client.upload_from_path('test.jpg', config=config, anon=None)
                            imagelink = image['link']
                    except:
                        imagelink = imageaddress
                        print(frontcolor.red('圖無法上傳QQ'))

                    #images = image[x]['src']

                    #variants = products[x]['variants']
                    #sizes_list = []
                    #for x in range(len(variants)):
                        #sizes_list.append('Size {}:'.format(variants[x]['title']) + str(url) + 'cart/{}:1'.format(variants[x]['id']))

                    price = products[x]['price']['current']['text']
                    currency = products[x]['price']['currency']
                    brand = products[x]['brandName']
                    chc = dollar(price,currency)
                    print(frontcolor.sky("Product Name:" + name + "\nLink:" + link + "\nprice:" + price + '\ncur:' + chc))
                    #api.push_message('Ub58162dabc1de9b209bdd89b34486d62',TextSendMessage(text= name + "\nLink:" + link + "\nPrice:" + price ))
                    if any(kw in name.lower() for kw in keyword):
                        webhook = DiscordWebhook(url=webhook_url, content='')
                        embed = DiscordEmbed(title=name, color=random.randint(0, 16777215), url=link)
                        embed.add_embed_field(name='**產品名稱：**',value= name)
                        embed.add_embed_field(name='**品牌：**', value=brand)
                        embed.add_embed_field(name='**售價：**', value=price + '\n' + '幣別：' + currency)
                        embed.add_embed_field(name ='**金額(TWD)：**',value = chc)
                        embed.set_thumbnail(url = imagelink)
                        embed.set_footer(text='ASOS Monitor By Wang')
                        webhook.add_embed(embed)
                        webhook.execute()
                        time.sleep(3)

if __name__ == "__main__":
    webhook_url = 'https://canary.discordapp.com/api/webhooks/674297005362905088/Y5E_A6w7T3-fwSkDZqZrJcml0Gnm1OLE7lKF-_HqU2Yuqj0Mu_H61O20zUMhjn7KFP0I'

    sitelist = read_from_txt('asossitelist.txt')

    keyword = []

    with open('keyword.txt','r') as k:
        key = k.read().split(',')
        for kw in key:
            keyword.append(kw)

    if len(keyword) > 1:
        print('關鍵字為: {}\n'.format(', '.join(keyword)))
    else:
        print('沒有關鍵字\n')

    for url in sitelist:
        t = Thread(target=newp, args=[url])
        t.start()
        time.sleep(1)
