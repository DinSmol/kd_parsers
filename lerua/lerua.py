import csv
import datetime
import os
import re
import time
import random

import requests
from bs4 import BeautifulSoup

import schedule

head_link = 'https://leroymerlin.ru'
base_link = 'https://leroymerlin.ru/catalogue/'
result = []


class ConSite():
	def __init__(self):
		self.date_create = datetime.datetime.now().date()
		self.sources = []
		self.debug = True

	'''get list of category urls in catalog'''

	def get_delay(self):
		return 1 + (random.random() * 1)

	def get_category_urls(self, url):
		self.page = requests.get(url)
		self.soup = BeautifulSoup(self.page.text, 'html.parser')
		data = self.soup.find_all("aside", {"class": "catalog-left-panel"})

		for x in data:
			
			middle = x.find_all('li')

			for temp_url in middle:
				sub_url = temp_url.find('a').attrs['href']
				sub_url = head_link + sub_url
				self.get_sub_urls(sub_url)

	def get_sub_urls(self, url):
		time.sleep(self.get_delay())
		self.page = requests.get(url)
		self.soup = BeautifulSoup(self.page.text, 'html.parser')
		cards = self.soup.find_all("div", {"class": "section-card"})

		if cards:
			for card in cards:
				temp_title = card.find("div", {"class": "title"}).text
				print(temp_title)
				lies = card.find_all("li")

				for li in lies:
					if li:
						try:
							link = li.find('a').attrs['href']
							name = li.find("span", {"class": "section-card-text"}).text
							self.get_sub_urls(head_link + link)
						except AttributeError:
							print(li.text)
							break
						except Exception as e:
							print(link, e.__class__)
							import pdb; pdb.set_trace()
							break
		else:
			title = self.soup.find("div", {"class": "page-title"})
			title = title.find('h1').text
			self.get_content(title, url)

	def check_next_page(self, soup, url):
		next_page = None
		
		try:
			paginator = soup.find("div", {"class": "next-paginator-button-wrapper"})
			next_page = paginator.find('a', {"class": "paginator-button"}).attrs['href']
		except KeyError:
			try:
				paginator = soup.find("div", {"class": "next-paginator-button-wrapper"})
				next_page = paginator.attrs['href']
			except Exception as e:
				print(f'Some trouble {e.__class__}')
				pass

		except AttributeError:
			'''next page is not exist'''
			pass

		if next_page:
			return head_link + next_page
		return None

	def get_content(self, title, url):
		time.sleep(self.get_delay())
		self.page = requests.get(url)
		self.soup = BeautifulSoup(self.page.text, 'html.parser')

		next_page = self.check_next_page(self.soup, url)

		print(title, url)
		result.append(url)	#  add url to result list

		if next_page:
			self.get_content(title, next_page)


obj = ConSite()

def task():
	'''comment try block if you don't need to overwrite output file'''
	try:
		os.remove('output.csv')
	except FileNotFoundError:
		print('Nothing to delete')

	print('Processing...')
	sub_urls = obj.get_category_urls(base_link)

	'''write data to csv file'''
	with open('output.csv', 'a', newline='') as csvfile:
		writer = csv.writer(csvfile)

		for item in result:
			writer.writerow([item])

	current_date = datetime.datetime.now().date()
	print(f'Report is ready! ({current_date})')


'''run task by schedule'''
# shedule.every().monday.do(task)   #run task every monday
# shedule.every().hour.do(task)   #run task every hour
# shedule.every().day.at("10:00").do(task)   #run task every day at 10:00
schedule.every(5).minutes.do(task)  # run task every 5 minutes

'''comment this for use schedule'''
task()

'''uncomment this for use schedule'''
# '''main cycle'''
# while True:
# 	schedule.run_pending()
# 	time.sleep(1)
