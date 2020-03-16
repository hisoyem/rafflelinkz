import requests
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed
import sqlite3 as lite
import time, datetime



URL = 'https://rafflelinkz.com/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
			AppleWebKit/537.36 (KHTML, like Gecko)\
			Chrome/80.0.3987.122 Safari/537.36',
			'accept': '*/*'}
WEBHOOK = ''

while True:

	def get_all_links():
		"""Получаем все ссылки на раффлы
			с главной страницы"""

		# Уведомление о том, что все началось
		print("Start getting links from the home page...")

		# Создаем объект soup для работы с DOM-деревом главной страницы
		response = requests.get(URL, headers=HEADERS, params=None)
		# Если соединение установлено, то вернуть список с ссылками
		if response.status_code == 200:
			soup = BeautifulSoup(response.text, "lxml")
			# Контейнеры, в которых содержатся остальные теги 
			div_container = main_div = soup.find_all("div", class_="elementor-widget-container")
			# Список тегов с раффлами
			article_list = div_container[1].findChildren("article")
			# Список с ссылками
			link_list = []
			# Получаем ссылки с раффлами в чистом виде и добавляем в список
			for i in range(len(article_list)):
				link_list.append(article_list[i].find("a").get("href"))

			return link_list

	def get_links_from_db():
		"""Открываем соединение с БД и получаем 
			ссылки, которые в ней уже хранятся"""

		# В этой переменной будут храниться результаты запроса
		links_in_db = []

		# Подключаемся к БД и в links_in_db вытаскиваем данные
		conn = lite.connect('raffle.db')
		with conn:
			cur = conn.cursor()
			sql_select = "SELECT link FROM information"
			cur.execute(sql_select)
			links_in_db = cur.fetchall()
		conn.close()
		links_in_db = [i[0] for i in links_in_db]    # Избавиться от вложенности

		return links_in_db

	def online_instore_webhook(img_url, raffle_name, shop_name, raffle_type, soup, raffle_url):
		"""Получить недостающие данные и отправить вебхук"""

		# Тут ссылки на раффлы, их может быть несколько либо 0
		p = soup.find('p').findChildren()
		# Список ссылок на раффлы
		links_in_p_tag = []
		for i in p:
			# Избегаем пустых строк между ссылками
			if len(i.text) != 0:
				links_in_p_tag.append(i.text)
		print("Links:", links_in_p_tag, '\n')
		# Отправляем вебхук
		webhook = DiscordWebhook(url=WEBHOOK)
		
		# create embed object for webhook
		embed = DiscordEmbed(title=raffle_name, 
							description="[{0}]({1})".format("Click here if no links",
							raffle_url), color=10181046)

		# add embed object to webhook
		webhook.add_embed(embed)

		embed.set_author(name='Quasar Cook',
		                 icon_url='https://sun9-66.userapi.com/c856032/v856032229/1e2b12/JTB-w2_3DzI.jpg')
		embed.set_thumbnail(url=img_url)
		embed.add_embed_field(name='Type', value=raffle_type, inline=True)
		embed.add_embed_field(name='Store', value=shop_name, inline=True)

		# Добавить https://, если такой подстроки нет в ссылке
		for i in links_in_p_tag:
			if not "https://" in i:
				i = "https://" + i
			if len(links_in_p_tag) != 0:
				embed.add_embed_field(name="Link", value="[Click]({})".format(i), inline=True)
		embed.set_footer(text = 'Powered by Quasar Cook @hisoyem')

		response = webhook.execute()

		return insert_links_into_db(raffle_url)

	def app_webhhok(img_url, raffle_name, shop_name, raffle_type, soup, raffle_url):
		"""Вебхук для раффлов типа App"""

		response = requests.get(raffle_url, headers=HEADERS, params=None)

		appStore = None
		googlePlay = None

		if response.status_code == 200:
			soup = BeautifulSoup(response.text, 'lxml')
			app_buttons = soup.find_all("a", {"class": "app-button"})
			appStore = app_buttons[0]["href"]
			googlePlay = app_buttons[1]["href"]

		# Отправляем вебхук
		webhook = DiscordWebhook(url=WEBHOOK)
		
		# create embed object for webhook
		embed = DiscordEmbed(title=raffle_name, 
							description="[{0}]({1})".format("Click here if no links",
							raffle_url), color=10181046)

		# add embed object to webhook
		webhook.add_embed(embed)

		embed.set_author(name='Quasar Cook',
		                 icon_url='https://sun9-66.userapi.com/c856032/v856032229/1e2b12/JTB-w2_3DzI.jpg')
		embed.set_thumbnail(url=img_url)
		embed.add_embed_field(name='Type', value=raffle_type, inline=True)
		embed.add_embed_field(name='Store', value=shop_name, inline=True)
		embed.add_embed_field(name='App Store', value="[Download]({})".format(appStore), inline=True)
		embed.add_embed_field(name='Google Play', value="[Download]({})".format(googlePlay), inline=True)
		embed.set_footer(text = 'Powered by Quasar Cook @hisoyem')

		response = webhook.execute()

		return insert_links_into_db(raffle_url)

	def social_webhook(img_url, raffle_name, shop_name, raffle_type, soup, raffle_url):
		print("I'm in social")
		# Отправляем вебхук
		webhook = DiscordWebhook(url=WEBHOOK)
		
		# create embed object for webhook
		embed = DiscordEmbed(title=raffle_name, 
							description="[{0}]({1})".format("Click here if no links",
							raffle_url), color=10181046)

		# add embed object to webhook
		webhook.add_embed(embed)

		embed.set_author(name='Quasar Cook',
		                 icon_url='https://sun9-66.userapi.com/c856032/v856032229/1e2b12/JTB-w2_3DzI.jpg')
		embed.set_thumbnail(url=img_url)
		embed.add_embed_field(name='Type', value=raffle_type, inline=True)
		embed.add_embed_field(name='Store', value=shop_name, inline=True)
		embed.set_footer(text = 'Powered by Quasar Cook @hisoyem')

		response = webhook.execute()

		return insert_links_into_db(raffle_url)

	def insert_links_into_db(raffle_url):
		"""Функция вызвана из какой-либо функции
			отправки вебхука"""
		try:
			print("Inserting new link")
			conn = lite.connect('raffle.db')
			with conn:
				cur = conn.cursor()
				sql_insert = "INSERT INTO information (link)\
							VALUES (?)"
				cur.execute(sql_insert, (raffle_url, ))
			conn.close()
			print("New link inserted")
		except Exception as e:
			print("Insert failed")
			print("Esception:", e.name)

	def open_new_urls(diff):
		"""Открыть новые URL из списка сайтов, которых нет в БД"""

		# Итерируем список, проходимся по каждому сайту
		for i in diff:
			request = requests.get(i, headers=HEADERS, params=None)
			if request.status_code == 200:
				print(i, request.status_code)
				soup = BeautifulSoup(request.text, 'lxml')
				# Изображение для самбнейл
				img_for_thumbnail = soup.find("img", {"class": "lazyimages"})["data-src"]
				print("Image for thumbnail:", img_for_thumbnail)

				h1 = soup.find('h1')
				# Название раффла
				h1_text = h1.text
				print("Name of the raffle:", h1_text)

				div_meta = h1.find_next_siblings('div')[0]
				a_list = div_meta.find_all('a')
				# e.g. supply, instore
				a_list = [x.text.strip() for x in a_list]

				# Магазин
				shop = a_list[0] # e.g. Supply/DSM/Antonia
				print("Shop:", shop)

				# Тип раффла
				shop_type = a_list[1] # e.g. Instore/Mobile/App/Social
				print("Type of shop:", shop_type)

				if shop_type == "Online" or\
					shop_type == "Instore":
					online_instore_webhook(img_for_thumbnail, h1_text,
											shop, shop_type, soup, i)
				elif shop_type == "App":
					app_webhhok(img_for_thumbnail, h1_text,
								shop, shop_type, soup, i)
				elif shop_type == "Social":
					social_webhook(img_for_thumbnail, h1_text,
									shop, shop_type, soup, i)
				else:
					print("Таких функций для отправки вебхуков нет")
		print("Walked on sites, sleeping 10 seconds")
		time.sleep(5)

	def check_difference():
		"""Получить разницу между ссылками с сайта
			и ссылками с БД"""

		# Тут хранится разница в ссылках
		diff = list(set(get_all_links()).difference(set(get_links_from_db())))
		print('The difference is:', diff, '\n')
		if len(diff) != 0:
			return open_new_urls(diff)
		else:
			print("No links found\nSleeping 10 seconds\n")
			time.sleep(10)
	check_difference()
	
