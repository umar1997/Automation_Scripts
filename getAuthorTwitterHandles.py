from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as ec


chromeOptions = Options()

# chromeOptions.add_argument('start-maximized')
# chromeOptions.add_argument('--disable-extensions')
# chromeOptions.add_argument('--disable-notifications')
chromeOptions.add_argument('--headless')
# chromeOptions.add_experimental_option('prefs', { 'profile.default_content_setting_values.notifications': 2})
driver = webdriver.Chrome(executable_path="./chromedriver.exe", options=chromeOptions)

def getAuthorHandler(driver, link, news_source):

	if news_source == 'WSJ':
		driver.get(link)
		authorTwitterHandle = driver.find_element_by_xpath("//meta[@name='twitter:creator']").get_attribute("content")
		return authorTwitterHandle

	elif news_source == 'MarketWatch':
		driver.get(link)
		authorTwitterHandle = driver.find_element_by_xpath("//meta[@name='twitter:creator']").get_attribute("content")
		return authorTwitterHandle

	elif news_source == 'NYT':
		driver.get(link)
		href = driver.find_element_by_xpath("//span[@class = 'byline-prefix']//following-sibling::a").get_attribute("href")
		driver.get(href)
		try:
			authorTwitterHandle = driver.find_element_by_xpath("//div[@class = 'module-body']/ul/li/a/span").text
			return authorTwitterHandle
		except:
			return None

	elif news_source == 'CNBC':
		driver.get(link)
		authorTwitterHandle = driver.find_element_by_xpath("//meta[@name='twitter:creator']").get_attribute("content")
		return authorTwitterHandle

	elif news_source == 'Forbes':
		driver.get(link)
		authorTwitterHandle = driver.find_element_by_xpath("//meta[@name='twitter:creator']").get_attribute("content")
		return authorTwitterHandle




if __name__ == '__main__':

	chromeOptions = Options()
	chromeOptions.add_argument('start-maximized')
	chromeOptions.add_argument('--disable-extensions')
	chromeOptions.add_argument('--disable-notifications')
	chromeOptions.add_experimental_option('prefs', { 'profile.default_content_setting_values.notifications': 2})

	# chromeOptions.add_argument('--headless')
	driver = webdriver.Chrome(executable_path="./chromedriver.exe", options=chromeOptions)

	# news_source = 'WSJ'
	# link = 'https://www.wsj.com/articles/samsung-is-raking-in-cash-now-it-needs-to-spend-some-11611831567'

	# news_source = 'NYT'
	# link = 'https://www.nytimes.com/2021/01/26/business/dealbook/larry-fink-blackrock-climate.html'
	# link = 'https://www.nytimes.com/2021/01/27/business/gamestop-wall-street-bets.html'

	# news_source = 'MarketWatch'
	# link = 'https://www.marketwatch.com/story/the-fed-admits-the-economy-has-slowed-but-its-banking-on-vaccines-to-undo-damage-11611780891'
	
	# news_source = 'CNBC'
	# link = 'https://www.cnbc.com/2021/01/27/chamath-palihapitiya-closes-gamestop-position-but-defends-individual-investors-right-to.html'

	# news_source  = 'Forbes'
	# link = 'https://www.forbes.com/sites/tommybeer/2021/01/26/report-american-billionaires-have-added-more-than-1-trillion-in-wealth-during-pandemic/?sh=6d5f33302564'


	# CANT GET
	#######################
	# Does Not Exist
	# news_source = 'Fed in Print'
	# link = 'https://fedinprint.org/item/fedawp/89579/original'

	# Does Not Exist
	# news_source = 'BIS'
	# link = 'https://www.bis.org/publ/bppdf/bispap114.htm'

	# Paywall
	# news_source = 'Bloomberg'
	# link = 'https://www.bloomberg.com/news/articles/2021-01-28/dan-wang-on-china-s-mission-to-be-a-world-leader-in-semiconductors'

	# Paywall
	# news_source = "Financial Times"
	# link = 'https://www.ft.com/content/76f88fc4-a0c2-42dd-8419-5956477c4a4a'

	authorTwitterHandle = getAuthorHandler(driver, link, news_source)
	print('Author Twitter Handler: ', authorTwitterHandle)

	
