import os
import pandas as pd
from time import sleep
from parsel import Selector
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as ec


def write_to_csv(data,filename):
	if not os.path.isfile(filename):
		data.to_csv(filename)
	else: # else it exists so append without writing the header
		data.to_csv(filename, mode='a', header=False)

def sign_in(linkedin_username, linkedin_password, driver):
	
	driver.get('https://www.linkedin.com')

	username = driver.find_element_by_id('session_key')
	username.send_keys(linkedin_username)
	sleep(0.5)

	password = driver.find_element_by_id('session_password')
	password.send_keys(linkedin_password)
	sleep(0.5)

	sign_in_button = driver.find_element_by_xpath('//*[@type="submit"]')
	sign_in_button.click()
	sleep(5)

def get_details(addProfilesFilename, filename, driver):
	df_profiles = pd.read_csv(addProfilesFilename)
	profiles_list = list(df_profiles['Links'])
	
	profileName, jobTitle, company, university, city, linkedIn = [], [], [], [], [], []
	for profile in profiles_list:
		print('-'*20)
		print(profile)
		print('-'*20)
		driver.get(profile)
		sleep(5)

		baseUrl = "//main[@id='main']//div[@class='display-flex mt2']//"
		profileName.append(driver.find_element_by_xpath(baseUrl + "div[1]/ul[1]/li").text)
		try:
			jobTitle.append(driver.find_element_by_xpath(baseUrl + "div[1]/h2").text)
		except:
			jobTitle.append("-")
		try:
			city.append(driver.find_element_by_xpath(baseUrl + "div[1]/ul[2]/li").text)
		except:
			city.append("-")
		try:
			company.append(driver.find_element_by_xpath(baseUrl + "div[2]/ul/li[1]/a/span").text)
		except:
			company.append("-")
		try:
			university.append(driver.find_element_by_xpath(baseUrl + "div[2]/ul/li[2]/a/span").text)
		except:
			university.append("-")
		
		linkedIn.append(profile)

	df = pd.DataFrame()
	df['Candidate'] = profileName
	df['Job Title'] = jobTitle
	df['Company'] = company
	df['University'] = university
	df['City'] = city
	df['LinkedIn'] = linkedIn

	df.set_index('Candidate', inplace=True)
	write_to_csv(df,filename)

if __name__ == '__main__':
	
	path = os.path.abspath('')
	load_dotenv(os.path.join(path, '.env'))

	FILENAME = 'Profiles.csv'
	EMAIL = os.getenv("EMAIL")
	PASSWORD = os.getenv("PASSWORD")
	ADD_PROFILES = 'Add_Profiles.csv'

	chromeOptions = Options()

	# Comment out these
	chromeOptions.add_argument('start-maximized')
	chromeOptions.add_argument('--disable-extensions')
	chromeOptions.add_argument('--disable-notifications')
	# Disable browser notifications
	chromeOptions.add_experimental_option('prefs', { 'profile.default_content_setting_values.notifications': 2})

	# chromeOptions.add_argument('--headless')

	# chromeOptions.add_argument('--headless')
	driver = webdriver.Chrome(executable_path="./chromedriver.exe", options=chromeOptions)

	print('#'*20)
	print('Signing In...')
	sign_in(EMAIL, PASSWORD, driver)
	print('Fetching Details...')
	get_details(ADD_PROFILES, FILENAME, driver)
	print('#'*20)
	driver.quit()

