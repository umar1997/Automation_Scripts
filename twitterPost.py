import os
import re
import time
import schedule
import requests
import datetime
import dateutil.parser
from dotenv import load_dotenv
from operator import itemgetter

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as ec

HOURS = 12
TWITTER_THRESHOLD = 20

def postTweet(driver, article, authorTwitterHandle, newsSourceHandler):

	path = os.path.abspath('')
	load_dotenv(os.path.join(path, '.env'))

	EMAIL = os.getenv("EMAIL")
	PASSWORD = os.getenv("PASSWORD")
	USER_NAME = os.getenv("USER_NAME")

	driver.get("https://twitter.com/login")
	wait = WebDriverWait(driver, 10)

	username_input = wait.until(ec.visibility_of_element_located((By.NAME, "session[username_or_email]")))
	username_input.send_keys(EMAIL)

	password_input = wait.until(ec.visibility_of_element_located((By.NAME, "session[password]")))
	password_input.send_keys(PASSWORD)

	login_button = wait.until(ec.visibility_of_element_located((By.XPATH, "//div[@data-testid='LoginForm_Login_Button']")))
	login_button.click()

	error_bool = True
	try:
		error_message = wait.until(ec.visibility_of_element_located((By.XPATH, "//h1[@role='heading']//following-sibling::div/span")))
	except:
		error_bool = False

	if error_bool:
		username_input = wait.until(ec.visibility_of_element_located((By.NAME, "session[username_or_email]")))
		username_input.send_keys(USER_NAME)

		password_input = wait.until(ec.visibility_of_element_located((By.NAME, "session[password]")))
		password_input.send_keys(PASSWORD)

		login_button = wait.until(ec.visibility_of_element_located((By.XPATH, "//div[@data-testid='LoginForm_Login_Button']")))
		login_button.click()

	tweet_text_span = wait.until(ec.visibility_of_element_located((By.XPATH, "//div[@data-testid='tweetTextarea_0']/div/div/div")))
	tweet_text_span.click()

	tagList = [0,0,0]
	for i, tag in enumerate(article['articletags_set']):
		word = tag['tag']
		words = word.split(' ')
		words = [word.capitalize() for word in words]
		seperator = ''
		tagList[i] = seperator.join(words)

	print(tagList)
	newLine = "\n"
	if authorTwitterHandle == None and newsSourceHandler == None :
		tweet = (
			f"{article['title']}{newLine}"
			f"{newLine}"
			f"For More Trending Finance News,{newLine}"
			f"Please visit: www.mertium.com{newLine}"
			f"#{tagList[0]} #{tagList[1]} #{tagList[2]}{newLine}"
			f"{article['link']}"
			)
	elif authorTwitterHandle == None:
		tweet = (
			f"{article['title']}{newLine}"
			f"News Source: {newsSourceHandler}{newLine}"
			f"{newLine}"
			f"For More Trending Finance News,{newLine}" 
			f"Please visit: www.mertium.com{newLine}"
			f"#{tagList[0]} #{tagList[1]} #{tagList[2]}{newLine}"
			f"{article['link']}"
			)

	else:
		
		authorTwitterHandle = authorTwitterHandle.replace('@','') # If username has multiple @
		authorTwitterHandle = "@" + authorTwitterHandle

		tweet = (
			f"{article['title']}{newLine}"
			f"Author: {authorTwitterHandle}{newLine}"
			f"News Source: {newsSourceHandler}{newLine}"
			f"{newLine}"
			f"For More Trending Finance News,{newLine}" 
			f"Please visit: www.mertium.com{newLine}"
			f"#{tagList[0]} #{tagList[1]} #{tagList[2]}{newLine}"
			f"{article['link']}"
			)


	tweet_text_span.send_keys(tweet)

	# tweet_button = wait.until(ec.visibility_of_element_located((By.XPATH, "//div[@data-testid='tweetButtonInline']")))
	# tweet_button.click()

def getAuthorHandler(driver, article):

	news_source = article['news_source']
	link = article['link']

	print('News Source: ', news_source)
	print('Link: ', link)
	if news_source == 'WSJ':
		driver.get(link)
		try:
			authorTwitterHandle = driver.find_element_by_xpath("//meta[@name='twitter:creator']").get_attribute("content")
		except:
			authorTwitterHandle = None

	elif news_source == 'MarketWatch':
		driver.get(link)
		try:
			authorTwitterHandle = driver.find_element_by_xpath("//meta[@name='twitter:creator']").get_attribute("content")
		except:
			authorTwitterHandle = None

	elif news_source == 'NYT':
		driver.get(link)
		try:
			href = driver.find_element_by_xpath("//span[@class = 'byline-prefix']//following-sibling::a").get_attribute("href")
			driver.get(href)
			try:
				authorTwitterHandle = driver.find_element_by_xpath("//div[@class = 'module-body']/ul/li/a/span").text
			except:
				authorTwitterHandle = None
		except:
			authorTwitterHandle = None

	elif news_source == 'CNBC':
		driver.get(link)
		try:
			authorTwitterHandle = driver.find_element_by_xpath("//meta[@name='twitter:creator']").get_attribute("content")
		except:
			authorTwitterHandle = None

	elif news_source == 'Forbes':
		driver.get(link)
		try:
			authorTwitterHandle = driver.find_element_by_xpath("//meta[@name='twitter:creator']").get_attribute("content")
		except:
			authorTwitterHandle = None	

	else:
		authorTwitterHandle = None

	return authorTwitterHandle

def getNewsSourceHandler(article):
	news_source = article['news_source']
	newsSites = ['Financial Times', 'CNBC', 'WSJ', 'NYT', 'Forbes', 'Seeking Alpha', 'Bloomberg', 'MarketWatch']
	newsHandlers = ['@FT', '@CNBC', '@WSJ', '@nytimes', '@Forbes', '@SeekingAlpha', '@markets', '@MarketWatch']
	if news_source in newsSites:
		index = newsSites.index(news_source)
		return newsHandlers[index]
	else:
		return None


def getArticles():
	URL = 'http://mertium.com/api/news/trending/articles/last/week/'
	r = requests.get(url = URL)
	data = r.json()

	now = datetime.datetime.now(dateutil.tz.tzoffset(None, -18000))
	one_day_before = now - datetime.timedelta(hours=HOURS)
	
	articlesNotChosenCount = 0
	articles = []
	while True:
		
		for index in range(len(data['results'])):
			
			article = {}
			headline = data['results'][index]['title']
			headline = headline.replace('&#39;', '\'')
			article['title'] = headline
			article['news_source'] = data['results'][index]['news_source']
			time = dateutil.parser.parse(data['results'][index]['timestamp'])
			article['timestamp'] = time
			article['link'] = data['results'][index]['link']
			article['twitter_score'] = data['results'][index]['tweet_count']
			article['articletags_set'] = data['results'][index]['articletags_set']

			if (time > one_day_before) and (len(article['articletags_set']) == 3) and (article['twitter_score'] >= TWITTER_THRESHOLD):
				articles.append(article)
			else:
				articlesNotChosenCount += 1

		URL = data['next']
		r = requests.get(url = URL)
		data = r.json()
		
		if data['next'] == None:
			for index in range(len(data['results'])):
			
				article = {}
				headline = data['results'][index]['title']
				headline = headline.replace('&#39;', '\'')
				article['title'] = headline
				article['news_source'] = data['results'][index]['news_source']
				time = dateutil.parser.parse(data['results'][index]['timestamp'])
				article['timestamp'] = time
				article['link'] = data['results'][index]['link']
				article['twitter_score'] = data['results'][index]['tweet_count']
				article['articletags_set'] = data['results'][index]['articletags_set']
				
				if (time > one_day_before) and (len(article['articletags_set']) == 3) and (article['twitter_score'] >= TWITTER_THRESHOLD):
					articles.append(article)
				else:
					articlesNotChosenCount += 1


			break

	articles.sort(key = itemgetter('twitter_score') , reverse= True)
	print('Articles Chosen: ', len(articles))
	print('Articles Not Chosen: ', articlesNotChosenCount)	
	return articles


def job(articlesDict):

	print('\n')
	now = datetime.datetime.now(dateutil.tz.tzoffset(None, -18000))
	one_day_before = now - datetime.timedelta(hours=HOURS)
	print('########################################')
	print(now)
	print(one_day_before)
	print('Retrieving Articles...')
	articles = getArticles()
	print('# Of Articles: ', len(articles))
	if len(articles) != 0:

		post_article = None
		for a in range(len(articles)):

			if articles[a]['title'] not in articlesDict:
				post_article = articles[a]
				articlesDict[articles[a]['title']] = articles[a]['timestamp']
				break

		keyList = list(articlesDict)
		for key in keyList:
			if one_day_before > articlesDict[key]:
				try:
					articlesDict.pop(key)
				except:
					print(key, "---------------------- DOES NOT EXIST")
		
		if post_article != None:

			chromeOptions = Options()

			# Comment out these
			chromeOptions.add_argument('start-maximized')
			chromeOptions.add_argument('--disable-extensions')
			chromeOptions.add_argument('--disable-notifications')
			# Disable browser notifications
			chromeOptions.add_experimental_option('prefs', { 'profile.default_content_setting_values.notifications': 2})

			# chromeOptions.add_argument('--headless')
			driver = webdriver.Chrome(executable_path="./chromedriver.exe", options=chromeOptions)

			print(articlesDict)
			print('Article To Be Posted....')
			print(post_article)
			print('Getting News Source Handler...')
			newsSourceHandler = getNewsSourceHandler(post_article)
			print('Getting Author Handler...')
			authorTwitterHandle = getAuthorHandler(driver, post_article)
			print('News Source: ', newsSourceHandler)
			print('Author Handler: ', authorTwitterHandle)
			print('Posting On Twitter...')
			postTweet(driver, post_article, authorTwitterHandle, newsSourceHandler)
			print('Article Posted...')
		else:
			print('All Articles have with Score >= 20 have been posted')
	else:
		print('No Articles in Last 3 Hrs with Twitter Score >= 20')





if __name__ == '__main__':
	print('Server Started...')
	
	articlesDict = {}
	# schedule.every(3).hour.do(job, articlesDict)
	schedule.every(1).minutes.do(job, articlesDict)
	while True:
		schedule.run_pending()
		time.sleep(1)
