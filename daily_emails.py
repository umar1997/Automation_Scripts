import time
import smtplib
import schedule
from string import Template
from email.message import EmailMessage

import requests
import datetime
from operator import itemgetter
import dateutil.parser

from string import Template
from jinja2 import Environment, BaseLoader


path = os.path.abspath('')
load_dotenv(os.path.join(path, '.env'))

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

HOURS = 24

def get_articles():
	URL = 'http://mertium.com/api/news/trending/articles/last/week/'
	r = requests.get(url = URL)
	data = r.json()

	articles = []
	repeated_articles = []
	titles_set = set()
	page = 1
	now = datetime.datetime.now(dateutil.tz.tzoffset(None, -18000))
	one_day_before = now - datetime.timedelta(hours=HOURS)
	while True:
		
		for index in range(len(data['results'])):
			
			article = {}
			article['title'] = data['results'][index]['title']
			article['news_source'] = data['results'][index]['news_source']
			time = data['results'][index]['timestamp']
			time = dateutil.parser.parse(time)
			article['timestamp'] = time
			article['timestamp_clean'] = time.strftime("%m/%d/%Y, %H:%M:%S")
			article['link'] = data['results'][index]['link']
			article['trending_score'] = data['results'][index]['trending_score']
			
			if article['title'] in titles_set:
				repeated_articles.append(article['title'])
			else:
				if time > one_day_before:
					articles.append(article)
			titles_set.add(article['title'])
		# print(page)
		page += 1
		URL = data['next']
		r = requests.get(url = URL)
		data = r.json()
		
		if data['next'] == None:
			
			for index in range(len(data['results'])):
				article = {}
				article['title'] = data['results'][index]['title']
				article['news_source'] = data['results'][index]['news_source']
				time = data['results'][index]['timestamp']
				time = dateutil.parser.parse(time)
				article['timestamp'] = time
				article['timestamp_clean'] = time.strftime("%m/%d/%Y, %H:%M:%S")
				article['link'] = data['results'][index]['link']
				article['trending_score'] = data['results'][index]['trending_score']
				
				if article['title'] in titles_set:
					repeated_articles.append(article['title'])
				else:
					if time > one_day_before:
						articles.append(article)
				titles_set.add(article['title'])
			break
	
	print('# of Articles: ', len(articles))
	articles.sort(key = itemgetter('trending_score') , reverse= True)		
	return articles

def job():

	date = datetime.datetime.today().strftime('%Y-%m-%d')
	print(date)
	print('Job Started...')

	contacts = ['mertium.news@gmail.com', 'mujahidmurtaza79@gmail.com', 'ejazk1500@gmail.com', 'husnainking1110@gmail.com', 'ndmrahmat@gmail.com', 'yusrahamid07@gmail.com']

	# HEADER
	msg = EmailMessage()
	msg['Subject'] = 'Mertium Top Trending Daily News'
	msg['From'] = EMAIL_ADDRESS
	msg['To'] = ', '.join(contacts)

	# CONTENT
	msg.set_content('Contact Mertium Team If No Headlines Are Recieved.')

	print('Getting Articles...')
	articles_list = get_articles()[:10]
	print('Articles Retrieved...')

	# HTML
	html_template = """\
	<!DOCTYPE html>
	<html>
		<body>
		<div>
			<h1 style="color:SlateGray;">Top Trending Articles</h1>
			<p> Top 10 Trending Finance Stories in Last 24 Hrs. </p>
			<ol>
			{% for article in articles %}
				<li><h3> {{ article['title'] }} </h3></li>
				<p> {{ article['news_source'] }} </p>
				<p> {{ article['link'] }} </p>
				<p> {{ article['timestamp_clean'] }} </p>
			{% endfor %}
			</ ol>
				
		<div>
		</body>
	</html>
	"""

	template = Environment(loader=BaseLoader).from_string(html_template)
	template_vars = {"articles": articles_list ,}
	html = template.render(template_vars)

	msg.add_alternative(html, subtype='html')

	with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
		smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
		print('Logged In Successfully...')

		smtp.send_message(msg)
		print('Email Sent...')


schedule.every().day.at("09:00").do(job) # 2:00  PST
# schedule.every().friday.at("10:00").do(job)
# schedule.every(1).minutes.do(job)
print('Server Started...')
while True:
	schedule.run_pending()
	time.sleep(1)