from lxml import html
import requests
import os
import sys
import unittest
from collections import Counter
import matplotlib.pyplot as plt

class DaftScrape:

	def __init__(self, web, fOut, state):
		self.web = web
		self.fOut = fOut
		self.state = state

	def standardise_price(self, value):
		return str(value).replace('\n', '').replace('\r', '').replace(',', '').replace('Price On Application', '').replace('Reserve:', '').replace('AMV:', '').replace('€', '').strip()

	def standardise_address(self, value):
		return str(value).replace('\n', '').replace('\r', '').replace(',', ' |').strip()

	def standardise(self, value):
		return str(value).replace('\n', '').replace('\r', '').strip()

	def createString(self, listKeys):
		self.string = 'NULL'
		for key in listKeys: self.string = self.string + ',' + self.standardise(str(key))
		self.string = (self.string + '\n').lstrip(',')
		return self.string

	def existance(self):
		if os.path.isfile(self.fOut) == True:
			self.writeOut = open(self.fOut, 'a', encoding = 'utf-8')
		else:
			self.writeOut = open(self.fOut, 'a', encoding = 'utf-8')
			self.writeOut.write('price,address,bedrooms,bathrooms,type,county,page_no\n')

	def connect(self, starting):
		self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
		self.response = requests.get(self.web + str(starting), headers = self.headers)
		if self.response.status_code == 200:
			return html.fromstring(self.response.content)
	
	def listClean(self, values):
		temp = []
		for val in values:
			val = str(val).replace('\n', '').replace('\r', '').replace('AMV:', '').strip()
			if len(val) > 0 and not val.startswith('€'):
				temp.append(val)
		return temp

	def daft(self):
		self.existance()
		print ('Scraping: County ', self.state)
		for house_list in range(0, 100, 20):
			self.response = self.connect(house_list)

			try: self.trigger = self.response.xpath('//*[@id="gc_content"]/h1//text()')[0]
			except: self.trigger = True

			if self.trigger:

				if len(self.response.xpath('//div[contains(@class, "FeaturedCardPropertyInformation__detailsContainer")]')) != 0: self.activate = 'featured'
				else: self.activate = 'standard'

				if self.activate == 'featured':
					self.prices = self.response.xpath('//*[contains(@class, "FeaturedCardPropertyInformation__detailsContainer")]/div[1]/div[1]/a/strong//text()')
					self.address_1 = self.response.xpath('//*[contains(@class, "FeaturedCardPropertyInformation__detailsContainer")]/div[1]/div[2]/a//text()')
					self.bedrooms = self.response.xpath('//*[contains(@class, "FeaturedCardPropertyInformation__detailsContainer")]/div[1]/div[3]/a/div[1]/div//text()')
					self.bathrooms = self.response.xpath('//*[contains(@class, "FeaturedCardPropertyInformation__detailsContainer")]/div[1]/div[3]/a/div[2]/div//text()')
					self.type = self.response.xpath('//*[contains(@class, "FeaturedCardPropertyInformation__detailsContainer")]/div[1]/div[3]/a/div[3]//text()')
				else:
					self.prices = self.response.xpath('//*[contains(@class, "StandardPropertyInfo__detailsContainer")]/div[1]/div[1]/a/strong//text()')
					self.address_1 = self.listClean(self.response.xpath('//*[contains(@class, "StandardPropertyInfo__detailsContainer")]/div[1]/div[2]/a//text()'))
					self.bedrooms = self.response.xpath('//*[contains(@class, "StandardPropertyInfo__detailsContainer")]/div[1]/div[3]/a/div[1]/div//text()')
					self.bathrooms = self.response.xpath('//*[contains(@class, "StandardPropertyInfo__detailsContainer")]/div[1]/div[3]/a/div[2]/div//text()')
					self.type = self.response.xpath('//*[contains(@class, "StandardPropertyInfo__detailsContainer")]/div[1]/div[3]/a/div[3]//text()')

				for i in range(len(self.prices)):
					try:
						self.string = self.createString([	self.standardise_price(self.prices[i]), self.standardise_address(self.address_1[i]), 
						 									self.bedrooms[i], self.bathrooms[i], self.type[i], self.state, house_list])
						
						self.writeOut.write(self.string)
					except:
						pass
			else: continue

counties = ['Dublin', 'Meath', 'Kildare', 'Wexford']
for county in counties:
	DaftScrape(	state = county, 
				fOut = 'output.csv', 
				web = 'https://www.daft.ie/{}/property-for-sale/?s%5Badvanced%5D=1&s%5Bpt_id%5D%5B0%5D=1&s%5Bpt_id%5D%5B1%5D=2&s%5Bpt_id%5D%5B2%5D=3&s%5Bpt_id%5D%5B3%5D=4&s%5Bpt_id%5D%5B4%5D=6&searchSource=sale&offset='.format(county.lower())).daft()
