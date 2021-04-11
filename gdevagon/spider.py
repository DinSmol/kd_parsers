import datetime
import re
import csv

import requests
from bs4 import BeautifulSoup


class Spider():
    def __init__(self):
        self.date_create = datetime.datetime.now().date()  # can use for logging, if script will run by a schedule
        self.result = {}
        self.base_url = 'https://www.gdevagon.ru/scripts/info/way_info.php'
        self.page_url = 'https://www.gdevagon.ru/scripts/info/'
        self.links = set()
        self.info_url = 'https://www.gdevagon.ru'

    '''get and parse data from site'''
    def get_content(self, url):
        self.page = requests.get(url)
        self.soup = BeautifulSoup(self.page.text, 'html.parser')
        self.result['data'] = []
        self.result['info'] = []

        data = self.soup.find("table", {"class": "infot"})
        railways = data.find_all('tr')
        for item in railways:
            if item.find('a'):
                self.links.add(self.base_url + item.find('a').attrs['href'])
                self.get_links(self.base_url + item.find('a').attrs['href'])

        for link in self.links:
            self.page = requests.get(link)
            self.soup = BeautifulSoup(self.page.text, 'html.parser')
            try:
                data = self.soup.find_all("table", {"class": "infot"})[1].find_all('tr')
            except IndexError:
                print(f'Index error: {link}')

            for x in data:
                if x.find('a') and x.find('img'):
                    self.result['data'].append([x.find('td').text, x.find('a').text, x.find('a').attrs['href']])
                    print(f"Wrote data: {x.find('a').text}")

        self.get_geom()
        self.write_to_csv()
        print('Parsing is complete')

    def get_links(self, url):
        self.page = requests.get(url)
        self.soup = BeautifulSoup(self.page.text, 'html.parser')
        paginator = self.soup.find("span", {"class": "v2_page_listing"})
        if paginator:
            pages_data = paginator.find_all('a')
            for item in pages_data:
                if item.attrs['href']:
                    if item.attrs.get('title') and item.attrs['title'] == 'Следующие 10 страниц':
                        self.get_links(self.page_url + item.attrs['href'])
                    else:
                        self.links.add(self.page_url + item.attrs['href'])


    def get_geom(self):
        for row in self.result['data']:
            try:
                self.page = requests.get(self.info_url + row[2])
                pattern = r'GeoPoint\(\d*.\d*,.\d*.\d*.\)'
                tt = re.findall(pattern, self.page.text)
                arr = tt[0].split(',')
                x, y = float(arr[0][9:]), float(arr[1][1:-1])
                self.result['info'].append([row[1].upper(), x, y])
                print(f'Get geom for: {row[1]} - [{x}, {y}]')
            except Exception as e:
                print(e.__class__)

    def write_to_csv(self):
        '''write data to csv file'''
        with open('output.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Code', 'Name', 'Link'])
            for item in self.result['info']:
                writer.writerow(item)

url = 'https://www.gdevagon.ru/scripts/info/way_info.php'
data_url = 'https://vagon.online/references/stations/1'
obj = Spider()
obj.get_content(url)
