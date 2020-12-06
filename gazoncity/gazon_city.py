import csv
import datetime
import os
import re
import time

import requests
from bs4 import BeautifulSoup

import schedule

base_link = 'https://gazoncity.ru'
class Item():
    def __init__(self,
                 name,
                 price,
                 desc,
                 category,
                 image=None,
                 code=None,
                 brand=None,
                 length=None,
                 weight=None,
                 high=None,
                 width=None,
                 link=None):
        self.name = name
        self.price = price
        self.image = base_link + image
        self.description = desc
        self.category = category
        self.code = code
        self.brand = brand
        self.length = length
        self.width = width
        self.high = high
        self.weight = weight
        self.link = link

    def __iter__(self):
        return iter([
            self.name,
            self.price,
            self.category,
            self.code,
            self.brand,
            self.length,
            self.width,
            self.high,
            self.weight,
            self.image,
            self.link,
            self.description]
        )

    def __str__(self):
        return str(self.name) + str(self.code)

result = []    
class ConSite():
    def __init__(self):
        self.date_create = datetime.datetime.now().date()
        self.sources = []
        
    '''get list of category urls in catalog'''
    def get_category_urls(self, url):
        urls = []
        self.page = requests.get(url)
        self.soup = BeautifulSoup(self.page.text, 'html.parser')
        data = self.soup.find_all("li", {"class": "dropdown"})

        for x in data: 
            middle = x.find_all('li', {'class', ''})
            for temp_url in middle:
                sub_url = temp_url.find('a').attrs['href']
                if 'catalog' in sub_url:
                    title = temp_url.find('a').attrs['title']
                    urls.append([title, sub_url])
        return self.get_all_urls(urls)

    def get_urls_list(self, cat, link):
        urls_list = []
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
        pages = soup.find_all("div", {"class": "item"})

        for item in pages:
            find_url = item.find('a').attrs['href']
            if 'catalog' in find_url and find_url != '/catalog/':
                title = item.find('img').attrs['alt']
                urls_list.append([title, cat, find_url])
        return urls_list

    def check_next_page(self, cat, link):
        next_page = None
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
        pages = soup.find_all("li", {"class": "next"})

        for item in pages:
            next_page = item.find('a').attrs['href']
        if next_page:
            return base_link + next_page
        return None

    def get_all_urls(self, urls):
        all_urls = []
        for url in urls:
            active_url = base_link + url[1]
            while active_url:
                all_urls.extend(self.get_urls_list(url[0], active_url))
                active_url = self.check_next_page(url[0], active_url)

        return all_urls


    '''get data from site'''
    def get_content(self, title, category, link, base_link=None):
        url = base_link + link
        self.page = requests.get(url)
        self.soup = BeautifulSoup(self.page.text, 'html.parser')
        data = self.soup.find_all("div", {"class": "item"})

        for x in data: 
            try:
                price = re.sub(' ', '', x.find('span', itemprop="price").get("content"))
                image = x.find('img', itemprop='image').attrs['src']
                desc = re.sub('\s+', ' ', x.find('div', itemprop='description').get_text())
            except AttributeError:
                continue

            props = x.find('table', {'class': 'props_table'})
            try:
                prop_text = props.get_text()
            except AttributeError:
                result.append(Item(
                    name=title,
                    price=price,
                    image=image,
                    desc=desc,
                    category=category,
                    link=url
                ))
                continue
            try:
                temp = re.search('Код\n+\t+\d+', prop_text).group(0)
                code = re.sub('Код\s+', '', temp)
            except AttributeError:
                code = None
            try:
                temp = re.search('Бренд\n+\t+\w+\t', prop_text).group(0)
                brand = re.sub('\t', '', re.sub('Бренд\s+', '', temp))
            except AttributeError:
                brand = None
            try:
                temp = re.search('Длина, м\n+\t+\d+\.*\d*', prop_text).group(0)
                length = re.sub('Длина, м\s+', '', temp)
            except AttributeError:
                length = None
            try:
                temp = re.search('Ширина, м\n+\t+\d+\.*\d*', prop_text).group(0)
                width = re.sub('Ширина, м\s+', '', temp)
            except AttributeError:
                width = None
            try:
                temp = re.search('Высота, см\n+\t+\d+\.*\d*', prop_text).group(0)
                high = re.sub('Высота, см\s+', '', temp)
            except AttributeError:
                high = None
            try:
                temp = re.search('Упаковка, кг\n+\t+\d+', prop_text).group(0)
                weight = re.sub('Упаковка, кг\s+', '', temp)
            except AttributeError:
                weight = None

            result.append(Item(
                name=title,
                price=price,
                image=image,
                desc=desc,
                category=category,
                code=code,
                brand=brand,
                length=length,
                width=width,
                high=high,
                weight=weight,
                link=url
            ))


obj = ConSite()

def task():
    '''comment try block if you don't need to overwrite output file'''
    try:
        os.remove('output.csv')
    except FileNotFoundError:
        print('Nothing to delete')

    print('Processing...')
    sub_urls = obj.get_category_urls('https://gazoncity.ru/catalog/')

    for cat in sub_urls:
        obj.get_content(*cat, base_link)

    '''write data to csv file'''
    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Наименование',
            'Цена руб.',
            'Категория',
            'Код',
            'Производитель',
            'Длина',
            'Ширина',
            'Высота',
            'Вес',
            'Ссылка на изображение',
            'Ссылка',
            'Описание'])
        for item in result:
            writer.writerow(list(item))

    current_date = datetime.datetime.now().date()
    print(f'Report is ready! ({current_date})')

'''run task by schedule'''
# shedule.every().monday.do(task)   #run task every monday
# shedule.every().hour.do(task)   #run task every hour
# shedule.every().day.at("10:00").do(task)   #run task every day at 10:00
schedule.every(5).minutes.do(task)  #run task every 5 minutes

'''main cycle'''
while True:
    schedule.run_pending()
    time.sleep(1)
