import re
import os
import time
import schedule
import datetime
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as ec

def postTweet(driver, youtubeLink):

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

	newLine = "\n"
	tweet = (
		f"Top 10 Trending Finance Stories in the Last 24 Hours.{newLine}" 
		f"For more Trending Finance News,{newLine}"
		f"Please visit: www.mertium.com{newLine}"
		f"{youtubeLink}"
		)


	tweet_text_span.send_keys(tweet)

	# tweet_button = wait.until(ec.visibility_of_element_located((By.XPATH, "//div[@data-testid='tweetButtonInline']")))
	# tweet_button.click()


def getYoutubeLink(driver):
	link = 'https://www.youtube.com/channel/UCLuKeHlGorwGFIP7Jvpg0ug'
	driver.get(link)

	# label = driver.find_element_by_xpath("//ytd-expanded-shelf-contents-renderer[@class='style-scope ytd-shelf-renderer']//*/h3/a").get_attribute("aria-label")
	# youtubeLink = driver.find_element_by_xpath("//ytd-expanded-shelf-contents-renderer[@class='style-scope ytd-shelf-renderer']//*/h3/a").get_attribute("href")

	try:
		youtubeLink = driver.find_element_by_xpath("//div[@id='play-button']//a").get_attribute("href")
		return youtubeLink
	except Exception as e:
		print(youtubeLink)
		print(e)
		return None

	

def job():
	chromeOptions = Options()

	# Comment out these
	chromeOptions.add_argument('start-maximized')
	chromeOptions.add_argument('--disable-extensions')
	chromeOptions.add_argument('--disable-notifications')
	# Disable browser notifications
	chromeOptions.add_experimental_option('prefs', { 'profile.default_content_setting_values.notifications': 2})


	# chromeOptions.add_argument('--headless')
	driver = webdriver.Chrome(executable_path="./chromedriver.exe", options=chromeOptions)

	now = datetime.datetime.now(datetime.timezone(datetime.timedelta(days=-1, seconds=68400)))
	date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
	print('#######################################')
	print(date_time)
	print('Getting Youtube Link...')
	youtubeLink = getYoutubeLink(driver)
	if youtubeLink!= None:
		print('Youtube Link: ', youtubeLink)
		print('Posting on Twitter...')
		postTweet(driver, youtubeLink)
	else:
		print('There was no link...')
	print('Done!')


if __name__ == '__main__':

	print('Server Started...')
	# schedule.every().day.at("14:00").do(job)
	schedule.every(1).minutes.do(job)
	while True:
		schedule.run_pending()
		time.sleep(1)
