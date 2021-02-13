import datetime
import os
import re
import time

import requests
from bs4 import BeautifulSoup

STATE_GOOD = 'Кровь имеется в достаточном количестве (ведётся заготовка донорской плазмы)' # lights_icon_3.png
STATE_BAD = 'Крови недостаточно и необходимо пополнение' # lights_icon_1.png
STATE_CRITICAL =  'Запас крови достиг критического минимума' # lights_icon_0.png
STATE_OK = 'Кровь имеется в достаточном количестве' # lights_icon_2.png


class ConSite():
    def __init__(self):
        self.date_create = datetime.datetime.now().date()
        self.result = {}

    def convert_status(self, status):
        if '0' in status:
            return STATE_CRITICAL
        elif '1' in status:
            return STATE_BAD
        elif '2' in status:
            return STATE_OK
        elif '3' in status:
            return STATE_GOOD
        return 'Unknown'

    '''get data from site'''
    def get_content(self, url):
        self.page = requests.get(url)
        self.soup = BeautifulSoup(self.page.text, 'html.parser')
        self.result['data'] = []
        
        data = self.soup.find_all("script")[16]
        blocks = re.findall('balloon.*[\n].*[\n].*[\n].*.png', data.text)
        for block in blocks:
            try:
                name = re.search(':\s+[\'\s+«»№\d\"()а-яА-Я\-,.]*', block).group(0)[2:]
                status = self.convert_status(re.search('icon_\d?\.png', block).group(0))
                self.result['data'].append([name, status])
            except AttributeError:
                print(f'Block: {block}')

    def display_data(self):
        print(self.result)


url = 'https://yadonor.ru/donorstvo/gde-sdat/map-lights/'
obj = ConSite()
obj.get_content(url)
obj.display_data()
