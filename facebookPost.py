import os
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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec

HOURS = 12
TWITTER_THRESHOLD = 20

def postPost(driver, article):
	wait = WebDriverWait(driver, 10)
	driver.get("https://www.facebook.com/")

	path = os.path.abspath('')
	load_dotenv(os.path.join(path, '.env'))

	FACEBOOK_EMAIL = os.getenv("FACEBOOK_EMAIL")
	FACEBOOK_PASSWORD = os.getenv("FACEBOOK_PASSWORD")

	Email = driver.find_element_by_id("email")
	Email.send_keys(FACEBOOK_EMAIL)
	Password = driver.find_element_by_id("pass")
	Password.send_keys(FACEBOOK_PASSWORD)
	LogIn = driver.find_element_by_xpath("//button[@name='login']").click()

	time.sleep(5)
	driver.get("https://www.facebook.com/MertiumFin")
	

	createPost = wait.until(ec.visibility_of_element_located((By.XPATH, "//div[@aria-label='Create Post']")))
	createPost.click()

	tagList = [0,0,0]
	for i, tag in enumerate(article['articletags_set']):
		word = tag['tag']
		words = word.split(' ')
		words = [word.capitalize() for word in words]
		seperator = ''
		tagList[i] = seperator.join(words)

	print(tagList)
	newLine = "\n"

	postText = (
			f"{article['title']}{newLine}"
			f"News Source: {article['news_source']}{newLine}"
			f"{newLine}"
			f"For More Trending Finance News,{newLine}" 
			f"Please visit: www.mertium.com{newLine}"
			f"#{tagList[0]} #{tagList[1]} #{tagList[2]}{newLine}"
			f"{article['link']}"
			)

	time.sleep(5)
	postArea = driver.switch_to.active_element
	postArea.send_keys(postText)
	time.sleep(5)
	# postClick = wait.until(ec.visibility_of_element_located((By.XPATH, "//form[count(@*)=1]//div[@aria-label='Post']")))
	# postClick.click()
	time.sleep(10)

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
			postPost(driver, post_article)
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