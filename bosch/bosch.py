import argparse
import csv
import random
import time
from subprocess import check_output

import pytesseract
import urllib3
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

user_id = 
username = 
password = 'pass'

button = 'BoschPrivacySettingsV2__button BoschPrivacySettingsV2__button--tertiary'


class handler:
	def __init__(self):
		self.starting = '0842ar121011'
		self.chrome_options = Options()
		self.chrome_options.add_argument("--enable-automation")
		self.chrome_options.add_argument(
			'--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"')
		self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
		self.my_list = []
		self.direct_urls = {}
		time.sleep(2)

	def reconnect(self):
		self.driver.close()
		self.driver = webdriver.Chrome(chrome_options=self.chrome_options)

	def navigate(self):
		self.driver.get('http://partner.bosch.de/ew/ru/')
		time.sleep(2)
		self.driver.switch_to.frame('topFrame')
		self.driver.find_element_by_class_name('BoschPrivacySettingsV2__button').click()
		self.driver.maximize_window()
		self.driver.find_element_by_name('kdnr').send_keys(user_id)
		self.driver.find_element_by_name('login').send_keys(username)
		self.driver.find_element_by_name('pin').send_keys(password)
		self.driver.find_element_by_id('LoginButton').click()


	def enter(self):
		time.sleep(2)
		solution = input()

		#entering captcha text
		txtbox1 = self.driver.find_element_by_name('0.1.9.11.19.1')
		txtbox1.send_keys(solution)
		time.sleep(1)

		#submit
		self.driver.find_element_by_name('0.1.9.11.19.3').click()

	#taking screenshot
	def take_screenshot(self):
		self.driver.save_screenshot('myfile.png')

	#cropping image
	def crop_image(self, location, size):
		image = Image.open('screenshot.png')
		x, y = location['x'], location['y']
		w, h = size['width'], size['height']
		image.crop((x, y, x+w, y+h)).save('output.png')

	#retrieving text
	def recover_text(self, filename):
		image = Image.open(filename)
		# r,g,b,a = image.split()			#removing the alpha channel
		# image = Image.merge('RGB',(r,g,b))
		return pytesseract.image_to_string(image)

	def get_delay(self):
		return 3 + (random.random() * 3)

	def get_sub_urls(self, url_list):
		for url in url_list:
			time.sleep(self.get_delay())
			self.driver.get(url)
		
			sub_cat = None
			try:
				sub_cat = self.driver.find_elements_by_id('categories')
				title = self.driver.find_element_by_class_name('titleWrapper').text

			except Exception as e:
				print(f'Exception: {e.__class__}')
				detail_list = self.driver.find_elements_by_xpath('// *[ @ id = "mainContent"] / section / table[*]')
				title = self.driver.find_element_by_class_name('titleWrapper')
				html = self.driver.find_element_by_tag_name('html')
				html.send_keys(Keys.END)

				for detail_url in detail_list:
					it = detail_url.find_element_by_class_name('product-info')
					name = it.text
					it = detail_url.find_element_by_class_name('product-title')
					link = it.get_attribute('href')
					self.my_list.append([title, name, link])
				continue

			cats = self.driver.find_elements_by_xpath('//div[@class="category" or @class="category right"]')
			cat_list = [x.find_element_by_tag_name('a').get_attribute('href') for x in cats]
			self.get_sub_urls(cat_list)


	def write_to_csv(self, array):
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
			for item in array:
				writer.writerow(item)


	def get_urls(self):
		'''find catalog'''
		time.sleep(self.get_delay())
		try:
			temp = self.driver.find_element_by_xpath('//*[@id="actor_nav"]/nav[1]/ul[1]/li[1]/a')
			temp.click()
		except Exception:
			import pdb; pdb.set_trace()
		time.sleep(self.get_delay())        
		self.driver.switch_to.frame(0)

		'''find categories'''
		cats = self.driver.find_elements_by_xpath('//div[@class="category" or @class="category right"]')

		'''list of categories'''
		cat_list = [x.find_element_by_tag_name('a').get_attribute('href') for x in cats]

		while len(cat_list):
			try:
				temp = self.driver.find_element_by_xpath('//*[@id="actor_nav"]/nav[1]/ul[1]/li[1]/a')
				temp.click()
			except Exception:
				pass
			time.sleep(self.get_delay())
			cat_list.clear()
			cats = self.driver.find_elements_by_xpath('//div[@class="category" or @class="category right"]')
			import pdb; pdb.set_trace()
			
			'''find categories'''
			cats = self.driver.find_elements_by_xpath('//div[@class="category" or @class="category right"]')
			for item in cats:
				temp_url = item.find_element_by_tag_name('a').get_attribute('href')
				desc = item.find_element_by_class_name('link-action').text

				if desc not in self.direct_urls.keys():
					cat_list.append([desc, temp_url])
            
			work_url = cat_list.pop()
			self.get_sub_urls([work_url[1]])
			self.direct_urls[work_url[0]] = work_url[1]
			self.reconnect()
			self.navigate()
			time.sleep(self.get_delay())
			try:
				temp = self.driver.find_element_by_xpath('//*[@id="actor_nav"]/nav[1]/ul[1]/li[1]/a')
				temp.click()
				self.driver.switch_to.frame(0)
			except Exception:
				pass

		self.write_to_csv(self.my_list)


def resolve(path):
    print("Resampling the Image")
    check_output(['convert', path, '-resample', '600', path])
    return pytesseract.image_to_string(Image.open(path))

if __name__ == '__main__':
	h = handler()
	h.navigate()
	h.enter()
	h.get_urls()
