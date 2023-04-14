# - *- coding: utf- 8 - *-
import telebot, sqlite3, time, datetime, requests, configparser, random
from telebot  import types, apihelper

config = configparser.ConfigParser()
#config.read("settings.ini")
#token    = config["tgbot"]["token"]
token = "5669179922:AAF9zGe9JjWpEkCttzd55haTGhIn666666"
get_id = "5615773666"
#get_id   = config["tgbot"]["admin_id"]
admin_id = []
if "," in get_id:
	get_id = get_id.split(",")
	for a in get_id:
		admin_id.append(int(a))
else:
	try:
		admin_id = [int(get_id)]
	except ValueError:
		admin_id =[0]
		print("*****Вы не указали админ ID*****")

bot = telebot.TeleBot(token)

admin_keyboard = telebot.types.ReplyKeyboardMarkup(True)
admin_keyboard.row("🎁 Купить", "ℹ️ FAQ")
admin_keyboard.row("ℹ️ Изменить FAQ 🖍")
admin_keyboard.row("📘 Добавить товар", "📙 Удалить товар")
admin_keyboard.row("📗 Добавить товары", "📕 Удалить все товары")
admin_keyboard.row("🔏 Изменить QIWI кошелёк", "🔐 Проверить QIWI кошелёк")

user_keyboard = telebot.types.ReplyKeyboardMarkup(True)
user_keyboard.row("🎁 Купить", "ℹ️ FAQ")
ignor_command = ["🎁 Купить", "ℹ️ FAQ", "ℹ️ Изменить FAQ 🖍", "📘 Добавить товар", "📙 Удалить товар", "📗 Добавить товары", "📕 Удалить все товары", "🔏 Изменить QIWI кошелёк", "🔐 Проверить QIWI кошелёк"]
####################################################################################################
#Проверка на существование БД, при отсутствие, создание и настройка
with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
	cur = con.cursor()
#Проверка товаров
	try:
		cur.execute("SELECT * FROM items")
		print("DB was found(1/4)")
	except sqlite3.OperationalError:
		print("DB was not found(1/4)")
		cur.execute("CREATE TABLE items(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, price INT, data TEXT)")
		print("DB 1 was create...")
#Проверка FAQ
	try:
		cur.execute("SELECT * FROM faq")
	except sqlite3.OperationalError:
		print("DB was not found(2/4)")
		cur.execute("CREATE TABLE faq(infa TEXT)")
	row = cur.fetchone()
	if row == None:
		cur.execute("DROP TABLE faq")
		cur.execute("CREATE TABLE faq(infa TEXT)")
		cur.execute("INSERT INTO faq VALUES('🔘 Информация. Измените её в главном меню.\n(Bot created by djimbox)')")
		print("DB 2 was create...")
	else:
		print("DB was found(2/4)")
#Проверка киви
	try:
		cur.execute("SELECT * FROM qiwi")
	except sqlite3.OperationalError:
		print("DB was not found(3/4)")
		cur.execute("CREATE TABLE qiwi(login TEXT, token TEXT)")
	row = cur.fetchone()
	if row == None:
		cur.executemany("INSERT INTO qiwi(login, token) VALUES (?, ?)", [("nomer", "token")])
		print("DB 3 was create...")
	else:
		print("DB was found(3/4)")
#Проверка пополнивших
	try:
		cur.execute("SELECT * FROM buyers")
		print("DB was found(4/4)")
	except sqlite3.OperationalError:
		print("DB was not found(4/4)")
		cur.execute("CREATE TABLE buyers(users TEXT, iditem TEXT, comment TEXT, amount TEXT, receipt TEXT, randomnum, data TEXT)")
		print("DB 4 was create...")
if con:
	con.close()
####################################################################################################


@bot.message_handler(commands=["start"])
def start_message(message):
	if message.from_user.id in admin_id:
		try:
			bot.send_message(message.chat.id, "🔹 Бот готов к использованию. 🔹\nЕсли не появились вспомогательные кнопки, введите /start", reply_markup = admin_keyboard)
		except requests.exceptions.ConnectionError:
			bot.send_message(message.chat.id, "🔹 Бот готов к использованию. 🔹\nЕсли не появились вспомогательные кнопки, введите /start", reply_markup = admin_keyboard)
	else:
		try:
			bot.send_message(message.chat.id, "🔹 Бот готов к использованию. 🔹\nЕсли не появились вспомогательные кнопки, введите /start", reply_markup = user_keyboard)
		except requests.exceptions.ConnectionError:
			bot.send_message(message.chat.id, "🔹 Бот готов к использованию. 🔹\nЕсли не появились вспомогательные кнопки, введите /start", reply_markup = user_keyboard)

@bot.message_handler(content_types=["text"])
def send_text(message):
	idss = []
	name = []
	if message.text == "🎁 Купить":
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			keyboard = types.InlineKeyboardMarkup()
			cur.execute("SELECT * FROM items")
			row = cur.fetchall()
			for i in row:
				idss.append(i[0])
				name.append(i[1])
			x = 0
			if len(idss) >= 1:
				with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
					cur = con.cursor()
					cur.execute("SELECT * FROM items")
					while True:
						x += 1
						row = cur.fetchone()
						if row == None:
							break
						if x <= 10:
							keyboard.add(types.InlineKeyboardButton(text = (str(row[1]) + " - " + str(row[3]) + " руб"), callback_data = "b_select_item_" + str(row[0]) + "|0"))
				if len(idss) > 10:
					keyboard.add(types.InlineKeyboardButton(text = "➡️Далее➡️", callback_data = "b_nextPage|10"))
				try:
					bot.send_message(message.chat.id, "🎁 Выберите товар", reply_markup = keyboard)
				except requests.exceptions.ConnectionError:
					bot.send_message(message.chat.id, "🎁 Выберите товар", reply_markup = keyboard)
			else:
				try:
					bot.send_message(message.chat.id, "🎁 Извиняемся, в данное время товары отсутствуют.", reply_markup = keyboard)
				except requests.exceptions.ConnectionError:
					bot.send_message(message.chat.id, "🎁 Извиняемся, в данное время товары отсутствуют.", reply_markup = keyboard)
	elif message.text == "ℹ️ FAQ":
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			cur.execute("SELECT * FROM faq")
			row = cur.fetchall()
		try:
			bot.send_message(message.chat.id, row[0])
		except requests.exceptions.ConnectionError:
			bot.send_message(message.chat.id, row[0])
	elif message.text == "🔐 Проверить QIWI кошелёк":
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			cur.execute("SELECT * FROM qiwi")
			checkQiwi = cur.execute("SELECT * FROM qiwi").fetchall()[0]
		request = requests.Session()
		request.headers["authorization"] = "Bearer " + checkQiwi[1]
		parameters = {"rows": 5, "operation" : "IN"}
		selectQiwi = request.get("https://edge.qiwi.com/payment-history/v2/persons/" + checkQiwi[0] + "/payments", params = parameters)
		if selectQiwi.status_code == 200:
			try:
				bot.send_message(message.from_user.id, "✅ QIWI кошелёк полностью функционирует")
			except requests.exceptions.ConnectionError:
				bot.send_message(message.from_user.id, "✅ QIWI кошелёк полностью функционирует")
		else:
			try:
				bot.send_message(message.from_user.id, "❗️  QIWI кошелёк не работает!\nКак можно скорее его замените")
			except requests.exceptions.ConnectionError:
				bot.send_message(message.from_user.id, "❗️  QIWI кошелёк не работает!\nКак можно скорее его замените")
	elif message.text == "ℹ️ Изменить FAQ 🖍":
		try:
			bot.send_message(message.from_user.id, "🔘 Введите новый текст для FAQ")
			bot.register_next_step_handler(message, change_faq)
		except requests.exceptions.ConnectionError:
			bot.send_message(message.from_user.id, "🔘 Введите новый текст для FAQ")
			bot.register_next_step_handler(message, change_faq)
	elif message.text == "📘 Добавить товар":
		try:
			bot.send_message(message.from_user.id, "📘 Введите название товара")
			bot.register_next_step_handler(message, add_item_name)
		except requests.exceptions.ConnectionError:
			bot.send_message(message.from_user.id, "📘 Введите название товара")
			bot.register_next_step_handler(message, add_item_name)
	elif message.text == "📗 Добавить товары":
		try:
			bot.send_message(message.from_user.id, "📗 Введите название товаров")
			bot.register_next_step_handler(message, add_items_name)
		except requests.exceptions.ConnectionError:
			bot.send_message(message.from_user.id, "📗 Введите название товаров")
			bot.register_next_step_handler(message, add_items_name)
	elif message.text == "📙 Удалить товар":
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			keyboard = types.InlineKeyboardMarkup()
			cur.execute("SELECT * FROM items")
			row = cur.fetchall()
			for i in row:
				idss.append(i[0])
				name.append(i[1])
			x = 0
			if len(idss) >= 1:
				with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
					cur = con.cursor()
					cur.execute("SELECT * FROM items")
					while True:
						x += 1
						row = cur.fetchone()
						if row == None:
							break
						if x <= 10:
							keyboard.add(types.InlineKeyboardButton(text = (str(row[1]) + " - " + str(row[3]) + " руб"), callback_data = "r_select_item_" + str(row[0]) + "|0"))
				if len(idss) > 10:
					keyboard.add(types.InlineKeyboardButton(text = "➡️Далее➡️", callback_data = "r_nextPage|10"))
				try:
					bot.send_message(message.chat.id, "🎁 Выберите товар для удаления: ", reply_markup = keyboard)
				except requests.exceptions.ConnectionError:
					bot.send_message(message.chat.id, "🎁 Выберите товар для удаления: ", reply_markup = keyboard)
			else:
				try:
					bot.send_message(message.chat.id, "🎁 Товары отсутствуют.", reply_markup = keyboard)
				except requests.exceptions.ConnectionError:
					bot.send_message(message.chat.id, "🎁 Товары отсутствуют.", reply_markup = keyboard)
	elif message.text == "📕 Удалить все товары":
		keyboard = types.InlineKeyboardMarkup()
		yes_key = types.InlineKeyboardButton(text = "❌ Да, удалить", callback_data = "r_yes_del_all_item_")
		no_key  = types.InlineKeyboardButton(text = "✅ Нет, отменить", callback_data = "r_no_del_all_item_")
		keyboard.add(yes_key, no_key)
		bot.send_message(message.from_user.id, "📕 Подтвердите удаление всех товаров:", reply_markup = keyboard)
	elif message.text == "🔏 Изменить QIWI кошелёк":
		try:
			bot.send_message(message.from_user.id, "🥝 Введите логин(номер) QIWI кошелька")
			bot.register_next_step_handler(message, change_qiwi_number)
		except requests.exceptions.ConnectionError:
			bot.send_message(message.from_user.id, "🥝 Введите логин(номер) QIWI кошелька")
			bot.register_next_step_handler(message, change_qiwi_number)
####################################################################################################

@bot.callback_query_handler(func = lambda call:True)
def callback_inline(call):
	idss 	= []
	name 	= []
	amounts = []
	try:
		remover = call.data.split("|")
		remover = int(remover[1])
		if remover < 0:
			remover = 0
	except:
		pass
####################################################################################################
#Удаление товаров
	if call.data == "r_nextPage|" + str(remover):
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			keyboard = types.InlineKeyboardMarkup()
			cur.execute("SELECT * FROM items")
			while True:
				row = cur.fetchone()
				if row == None:
					break
				idss.append(row[0])
				name.append(row[1])
				amounts.append(row[3])
			try:
				x = 0
				for a in range(remover, len(idss)):
					if x < 10:
						keyboard.add(types.InlineKeyboardButton(text = (str(name[a]) + " - " + str(amounts[a]) + " руб"), callback_data = "r_select_item_" + str(idss[a]) + "|" + str(remover)))
					x += 1
				if remover + 9 >= len(idss):
					keyboard.add(types.InlineKeyboardButton(text = "⬅️Назад⬅️", callback_data = "r_previousPage|" + str(remover - 10)))
				else:
					next_keyboard = types.InlineKeyboardButton(text = "➡️Далее➡️", callback_data = "r_nextPage|" + str(remover + 10))
					number_keyboard = types.InlineKeyboardButton(text = str(remover)[:1], callback_data = ".....")
					previous_keyboard = types.InlineKeyboardButton(text = "⬅️Назад⬅️", callback_data = "r_previousPage|" + str(remover - 10))
					keyboard.add(previous_keyboard, number_keyboard, next_keyboard)
				try:
					bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "🎁 Выберите товар для удаления: ",
									reply_markup = keyboard)
				except requests.exceptions.ConnectionError:
					bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "🎁 Выберите товар для удаления: ",
									reply_markup = keyboard)
			except IndexError:
				pass
		if con:
			con.close()
	elif call.data == "r_previousPage|" + str(remover):
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			keyboard = types.InlineKeyboardMarkup()
			cur.execute("SELECT * FROM items")
			while True:
				row = cur.fetchone()
				if row == None:
					break
				idss.append(row[0])
				name.append(row[1])
				amounts.append(row[3])
			try:
				x = 0
				for a in range(remover, len(idss)):
					if x < 10:
						keyboard.add(types.InlineKeyboardButton(text = (str(name[a]) + " - " + str(amounts[a]) + " руб"), callback_data = "r_select_item_" + str(idss[a]) + "|" + str(remover)))
					x += 1
				if remover <= 0:
					keyboard.add(types.InlineKeyboardButton(text = "➡️Далее➡️", callback_data = "r_nextPage|" + str(remover + 10)))
				else:
					next_keyboard = types.InlineKeyboardButton(text = "➡️Далее➡️", callback_data = "r_nextPage|" + str(remover + 10))
					number_keyboard = types.InlineKeyboardButton(text = str(remover)[:1], callback_data = ".....")
					previous_keyboard = types.InlineKeyboardButton(text = "⬅️Назад⬅️", callback_data = "r_previousPage|" + str(remover - 10))
					keyboard.add(previous_keyboard, number_keyboard, next_keyboard)
				try:
					bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "🎁 Выберите товар для удаления: ",
						reply_markup = keyboard)
				except requests.exceptions.ConnectionError:
					bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "🎁 Выберите товар для удаления: ",
						reply_markup = keyboard)
			except IndexError:
				pass
		if con:
			con.close()
	elif "r_select_item_" in call.data:
		msg = call.data[14:]
		msg = msg.split("|")
		remover = msg[1]
		msg = int(msg[0])
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			cur.execute("SELECT * FROM items")
			while True:
				row = cur.fetchone()
				if row == None:
					break
				if row[0] == msg:
					keyboard = types.InlineKeyboardMarkup()
					keyboard.add(types.InlineKeyboardButton(text = "📙 Удалить товар", callback_data = "r_del_item_" + str(row[0])))
					keyboard.add(types.InlineKeyboardButton(text = "⬅️ Назад", callback_data = "r_list_back_" + remover))
					try:
						bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "🏷 *Название товара:* `{0}`\n💵 *Стоимость товара:* `{1}`\n📜 *Описание товара:* `{2}`\n💾 *Данные товара:* `{3}`".format(row[1], row[3], row[2], row[4]),
							reply_markup = keyboard, parse_mode = "MARKDOWN")
					except requests.exceptions.ConnectionError:
						bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "🏷 *Название товара:* `{0}`\n💵 *Стоимость товара:* `{1}`\n📜 *Описание товара:* `{2}`\n💾 *Данные товара:* `{3}`".format(row[1], row[3], row[2], row[4]),
							reply_markup = keyboard, parse_mode = "MARKDOWN")
		if con:
			con.close()
	elif "r_list_back_" in call.data:
		remover = int(call.data[12:])
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			keyboard = types.InlineKeyboardMarkup()
			cur.execute("SELECT * FROM items")
			while True:
				row = cur.fetchone()
				if row == None:
					break
				idss.append(row[0])
				name.append(row[1])
				amounts.append(row[3])
			try:
				x = 0
				for a in range(remover, len(idss)):
					if x < 10:
						keyboard.add(types.InlineKeyboardButton(text = (str(name[a]) + " - " + str(amounts[a]) + " руб"), callback_data = "r_select_item_" + str(idss[a]) + "|" + str(remover)))
					x += 1
				if remover <= 0 and len(idss) >= 10:
					keyboard.add(types.InlineKeyboardButton(text = "➡️Далее➡️", callback_data = "r_nextPage|" + str(remover + 10)))
				elif remover <= 0 and len(idss) <= 10:
					pass
				elif remover + 9 >= len(idss):
					keyboard.add(types.InlineKeyboardButton(text = "⬅️Назад⬅️", callback_data = "r_previousPage|" + str(remover - 10)))
				elif remover >= 10 and len(idss) >= 10:
					next_keyboard = types.InlineKeyboardButton(text = "➡️Далее➡️", callback_data = "r_nextPage|" + str(remover + 10))
					number_keyboard = types.InlineKeyboardButton(text = str(remover)[:1], callback_data = ".....")
					previous_keyboard = types.InlineKeyboardButton(text = "⬅️Назад⬅️", callback_data = "r_previousPage|" + str(remover - 10))
					keyboard.add(previous_keyboard, number_keyboard, next_keyboard)
				try:
					bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "🎁 Выберите товар для удаления: ",
									reply_markup = keyboard)
				except requests.exceptions.ConnectionError:
					bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "🎁 Выберите товар для удаления: ",
									reply_markup = keyboard)
			except IndexError:
				pass
		if con:
			con.close()
	elif "r_no_del_all_item_" in call.data:
		try:
			bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "📕 Вы отменили удаление товаров.")
		except requests.exceptions.ConnectionError:
			bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "📕 Вы отменили удаление товаров.")
	elif "r_yes_del_all_item_" in call.data:
		with sqlite3.connect("shopBD.sqlite") as con:
			cur = con.cursor()
			all_items = cur.execute("SELECT * FROM items").fetchall()
			x = 0
			for row in all_items:
				cur.execute("DELETE FROM items WHERE id = ?", (row[0],))
				con.commit()
				x += 1
			try:
				bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "📕 Было удалено `{0}` товаров.".format(x), parse_mode = "MARKDOWN")
			except requests.exceptions.ConnectionError:
				bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "📕 Было удалено `{0}` товаров.".format(x), parse_mode = "MARKDOWN")
		if con:
			con.close()
	elif "r_del_item_" in call.data:
		msg = int(call.data[11:])
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			cur.execute("DELETE FROM items WHERE id = ?", (msg,))
			con.commit()
		if con:
			con.close()
		try:
			bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "✅ Товар был удалён.")
		except requests.exceptions.ConnectionError:
			bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "✅ Товар был удалён.")
####################################################################################################
#Покупка товаров
	elif call.data == "b_nextPage|" + str(remover):
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			keyboard = types.InlineKeyboardMarkup()
			cur.execute("SELECT * FROM items")
			while True:
				row = cur.fetchone()
				if row == None:
					break
				idss.append(row[0])
				name.append(row[1])
				amounts.append(row[3])
			try:
				x = 0
				for a in range(remover, len(idss)):
					if x < 10:
						keyboard.add(types.InlineKeyboardButton(text = (str(name[a]) + " - " + str(amounts[a]) + " руб"), callback_data = "b_select_item_" + str(idss[a]) + "|" + str(remover)))
					x += 1
				if remover + 9 >= len(idss):
					keyboard.add(types.InlineKeyboardButton(text = "⬅️Назад⬅️", callback_data = "b_previousPage|" + str(remover - 10)))
				else:
					next_keyboard = types.InlineKeyboardButton(text = "➡️Далее➡️", callback_data = "b_nextPage|" + str(remover + 10))
					number_keyboard = types.InlineKeyboardButton(text = str(remover)[:1], callback_data = ".....")
					previous_keyboard = types.InlineKeyboardButton(text = "⬅️Назад⬅️", callback_data = "b_previousPage|" + str(remover - 10))
					keyboard.add(previous_keyboard, number_keyboard, next_keyboard)
				try:
					bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "🎁 Выберите товар: ",
									reply_markup = keyboard)
				except requests.exceptions.ConnectionError:
					bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "🎁 Выберите товар: ",
									reply_markup = keyboard)
			except IndexError:
				pass
		if con:
			con.close()
	elif call.data == "b_previousPage|" + str(remover):
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			keyboard = types.InlineKeyboardMarkup()
			cur.execute("SELECT * FROM items")
			while True:
				row = cur.fetchone()
				if row == None:
					break
				idss.append(row[0])
				name.append(row[1])
				amounts.append(row[3])
			try:
				x = 0
				for a in range(remover, len(idss)):
					if x < 10:
						keyboard.add(types.InlineKeyboardButton(text = (str(name[a]) + " - " + str(amounts[a]) + " руб"), callback_data = "b_select_item_" + str(idss[a]) + "|" + str(remover)))
					x += 1
				if remover <= 0:
					keyboard.add(types.InlineKeyboardButton(text = "➡️Далее➡️", callback_data = "b_nextPage|" + str(remover + 10)))
				else:
					next_keyboard = types.InlineKeyboardButton(text = "➡️Далее➡️", callback_data = "b_nextPage|" + str(remover + 10))
					number_keyboard = types.InlineKeyboardButton(text = str(remover)[:1], callback_data = ".....")
					previous_keyboard = types.InlineKeyboardButton(text = "⬅️Назад⬅️", callback_data = "b_previousPage|" + str(remover - 10))
					keyboard.add(previous_keyboard, number_keyboard, next_keyboard)
				try:
					bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "🎁 Выберите товар: ",
									reply_markup = keyboard)
				except requests.exceptions.ConnectionError:
					bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "🎁 Выберите товар: ",
									reply_markup = keyboard)
			except IndexError:
				pass
		if con:
			con.close()
	elif "b_select_item_" in call.data:
		msg = call.data[14:]
		msg = msg.split("|")
		remover = msg[1]
		msg = int(msg[0])
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			cur.execute("SELECT * FROM items")
			while True:
				row = cur.fetchone()
				if row == None:
					break
				if row[0] == msg:
					keyboard = types.InlineKeyboardMarkup()
					keyboard.add(types.InlineKeyboardButton(text = "💰 Купить товар", callback_data = "buy_item_" + str(row[0])))
					keyboard.add(types.InlineKeyboardButton(text = "⬅️ Назад", callback_data = "b_list_back_" + remover))
					try:
						bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "🏷 *Название товара:* `{0}`\n💵 *Стоимость товара:* `{1}`\n📜 *Описание товара:* `{2}`".format(row[1], row[3], row[2]),
							reply_markup = keyboard, parse_mode = "MARKDOWN")
					except requests.exceptions.ConnectionError:
						bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "🏷 *Название товара:* `{0}`\n💵 *Стоимость товара:* `{1}`\n📜 *Описание товара:* `{2}`".format(row[1], row[3], row[2]),
							reply_markup = keyboard, parse_mode = "MARKDOWN")
		if con:
			con.close()
	elif "b_list_back_" in call.data:
		remover = int(call.data[12:])
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			keyboard = types.InlineKeyboardMarkup()
			cur.execute("SELECT * FROM items")
			while True:
				row = cur.fetchone()
				if row == None:
					break
				idss.append(row[0])
				name.append(row[1])
				amounts.append(row[3])
			try:
				x = 0
				for a in range(remover, len(idss)):
					if x < 10:
						keyboard.add(types.InlineKeyboardButton(text = (str(name[a]) + " - " + str(amounts[a]) + " руб"), callback_data = "b_select_item_" + str(idss[a]) + "|" + str(remover)))
					x += 1
				if remover <= 0 and len(idss) >= 10:
					keyboard.add(types.InlineKeyboardButton(text = "➡️Далее➡️", callback_data = "b_nextPage|" + str(remover + 10)))
				elif remover <= 0 and len(idss) <= 10:
					pass
				elif remover + 9 >= len(idss):
					keyboard.add(types.InlineKeyboardButton(text = "⬅️Назад⬅️", callback_data = "b_previousPage|" + str(remover - 10)))
				elif remover >= 10 and len(idss) >= 10:
					next_keyboard = types.InlineKeyboardButton(text = "➡️Далее➡️", callback_data = "b_nextPage|" + str(remover + 10))
					number_keyboard = types.InlineKeyboardButton(text = str(remover)[:1], callback_data = ".....")
					previous_keyboard = types.InlineKeyboardButton(text = "⬅️Назад⬅️", callback_data = "b_previousPage|" + str(remover - 10))
					keyboard.add(previous_keyboard, number_keyboard, next_keyboard)
				try:
					bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "🎁 Выберите товар: ",
									reply_markup = keyboard)
				except requests.exceptions.ConnectionError:
					bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "🎁 Выберите товар: ",
									reply_markup = keyboard)
			except IndexError:
				pass
		if con:
			con.close()
	elif "buy_item_" in call.data:
		msg = int(call.data[9:])
		IdItems = 0
		randomChar = [random.randint(1, 9)]
		randomFake = [random.randint(9999, 999999999999)]
		randomNumber = [random.randint(9999, 999999999999)]
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			cur.execute("SELECT * FROM qiwi")
			sendNumber = cur.execute("SELECT * FROM qiwi").fetchall()[0][0]
		if con:
			con.close()
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			cur.execute("SELECT * FROM items")
			while True:
				row = cur.fetchone()
				if row == None:
					break
				if msg == row[0]:
					sendItemsAmmo = row[3]
					IdItems = row[0]
		if con:
			con.close()
		if IdItems != 0: 
			sendComment  = "{0}|{1}.{2}.{3}.{4}".format(call.from_user.id, IdItems, randomNumber[0], randomChar[0], randomFake[0])
			sendRequests = "https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={0}&amountInteger={1}&amountFraction=0&extra%5B%27comment%27%5D={2}&currency=643&blocked%5B0%5D=sum&blocked%5B1%5D=comment&blocked%5B2%5D=account".format(sendNumber, sendItemsAmmo, sendComment)
			sendMessage  = "📦 *Покупка товара*\n🥝 Для оплаты, нажмите кнопку ниже.\n*🥝 Менять поля НЕ НУЖНО*, всё уже указано.\n`(Ссылку нужно открывать через браузер, а не приложение qiwi)`\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n🔅 *Номер:* `{0}`\n🔅 *Коментарий:* `{1}`\n🔅 *Сумма:* `{2}`\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n🔄 После оплаты нажмите на кнопку `Проверить оплату`".format(sendNumber, sendComment, sendItemsAmmo)
			check_keyboard = types.InlineKeyboardMarkup()
			check_keyboard.add(types.InlineKeyboardButton(text = "🌐 Перейти к оплате", url = sendRequests))
			check_keyboard.add(types.InlineKeyboardButton(text = "🔄 Проверить оплату", callback_data = f"checkPay|{randomNumber[0]}|{sendItemsAmmo}"))
			try:
				if len(str(sendNumber)) < 10:
					try:
						bot.send_message(call.message.chat.id, "Рады тому что вас заинтересовал каталог наших услуг . Мы работаем С новыми клиентами только через Гарант сервис Фриланс биржи kwork . По всем вопросам пишите нам в наш профиль на бирже https://kwork.ru/user/DOMOSTROI .", parse_mode = "MARKDOWN")
						if len(admin_id) > 1:
							for a in range(len(admin_id)):
								try:
									bot.send_message(admin_id[a], "❗️ Оплата не работает, срочно укажите новые киви данные ❗️")
								except requests.exceptions.ConnectionError:
									bot.send_message(admin_id[a], "❗️ Оплата не работает, срочно укажите новые киви данные ❗️")
						else:
							try:
								bot.send_message(admin_id[0], "❗️ Оплата не работает, срочно укажите новые киви данные ❗️")
							except requests.exceptions.ConnectionError:
								bot.send_message(admin_id[0], "❗️ Оплата не работает, срочно укажите новые киви данные ❗️")
					except requests.exceptions.ConnectionError:
						bot.send_message(call.message.chat.id, "Рады тому что вас заинтересовал каталог наших услуг . Мы работаем С новыми клиентами только через Гарант сервис Фриланс биржи kwork . По всем вопросам пишите нам в наш профиль на бирже https://kwork.ru/user/DOMOSTROI .", parse_mode = "MARKDOWN")
						if len(admin_id) > 1:
							for a in range(len(admin_id)):
								try:
									bot.send_message(admin_id[a], "❗️ Оплата не работает, срочно укажите новые киви данные ❗️")
								except requests.exceptions.ConnectionError:
									bot.send_message(admin_id[a], "❗️ Оплата не работает, срочно укажите новые киви данные ❗️")
						else:
							try:
								bot.send_message(admin_id[0], "❗️ Оплата не работает, срочно укажите новые киви данные ❗️")
							except requests.exceptions.ConnectionError:
								bot.send_message(admin_id[0], "❗️ Оплата не работает, срочно укажите новые киви данные ❗️")
				else:
					try:
						bot.send_message(call.message.chat.id, sendMessage, parse_mode = "MARKDOWN", reply_markup = check_keyboard)
					except requests.exceptions.ConnectionError:
						bot.send_message(call.message.chat.id, sendMessage, parse_mode = "MARKDOWN", reply_markup = check_keyboard)
			except ValueError:
				try:
					bot.send_message(call.message.chat.id, "Рады тому что вас заинтересовал каталог наших услуг . Мы работаем С новыми клиентами только через Гарант сервис Фриланс биржи kwork . По всем вопросам пишите нам в наш профиль на бирже https://kwork.ru/user/DOMOSTROI .", parse_mode = "MARKDOWN")
				except requests.exceptions.ConnectionError:
					bot.send_message(call.message.chat.id, "Рады тому что вас заинтересовал каталог наших услуг . Мы работаем С новыми клиентами только через Гарант сервис Фриланс биржи kwork . По всем вопросам пишите нам в наш профиль на бирже https://kwork.ru/user/DOMOSTROI .", parse_mode = "MARKDOWN")
		else:
			try:
				bot.send_message(call.message.chat.id, "❗️ Данный товар не был найден.", parse_mode = "MARKDOWN", reply_markup = admin_keyboard)
			except requests.exceptions.ConnectionError:
				bot.send_message(call.message.chat.id, "❗️ Данный товар не был найден.", parse_mode = "MARKDOWN", reply_markup = admin_keyboard)
	elif call.data.startswith("checkPay"):
		msg = call.data[9:]
		msg = msg.split("|")
		getCommentQiwi	= []
		getAmountQiwi	= []
		getReceintQiwi	= []
		getDateQiwi		= []
		
		getNomerQiwi	= []
		getItems		= 0
		sendBuy			= 0
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			checkQiwi = cur.execute("SELECT * FROM qiwi").fetchall()[0]
		if con:
			con.close()
		request = requests.Session()
		request.headers["authorization"] = "Bearer " + checkQiwi[1]
		parameters = {"rows": 10, "operation" : "IN"}
		selectQiwi = request.get("https://edge.qiwi.com/payment-history/v2/persons/" + checkQiwi[0] + "/payments", params = parameters)
		selectQiwi = selectQiwi.json()["data"]
		for a in range(len(selectQiwi)):
			getCommentQiwi.append(selectQiwi[a]["comment"])
			getAmountQiwi.append(selectQiwi[a]["sum"]["amount"])
			getReceintQiwi.append(selectQiwi[a]["txnId"])
			getDateQiwi.append(selectQiwi[a]["date"])
			getNomerQiwi.append(selectQiwi[a]["personId"])
		allCheck   = False
		yesOrNo    = True
		howChar    = 0
		getBalance = 0
		for b in range(len(getCommentQiwi)):
			if str(msg[0]) in str(getCommentQiwi[b]) and str(msg[1]) in str(getAmountQiwi[b]):
				howChar = b
				allCheck = True
				getPayer      = getCommentQiwi[b].split("|")
				getIdPayer    = getPayer[0]
				getDataPayer  = []
				tempDataPayer = getPayer[1].split(".")
				getDataPayer.append(tempDataPayer[0])
				getDataPayer.append(tempDataPayer[1])
				break
		if allCheck:
			splitComment = getCommentQiwi[b].split("|")
			with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
				cur = con.cursor()
				getBuyers = cur.execute("SELECT * FROM buyers").fetchall()
			if con:
				con.close()
			for c in range(len(getBuyers)):
				if str(getIdPayer) in str(getBuyers[c][0]) and str(splitComment[1]) in str(getBuyers[c][1]):
					yesOrNo = False
			if yesOrNo:
				with sqlite3.connect("shopBD.sqlite") as con:
					cur = con.cursor()
					getItems = cur.execute("SELECT * FROM items").fetchall()
				if con:
					con.close()
				for c in range(len(getItems)):
					if str(getDataPayer[0]) == str(getItems[c][0]):
						sendBuy = str(getItems[c][4])
				with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
					cur = con.cursor()
					cur.executemany("INSERT INTO buyers(users, iditem, comment, amount, receipt, randomnum, data) VALUES (?, ?, ?, ?, ?, ?, ?)", [(splitComment[0], splitComment[1], getCommentQiwi[howChar], getAmountQiwi[howChar], getReceintQiwi[howChar], getDataPayer[1], getDateQiwi[howChar])])
				if con:
					con.close()
				with sqlite3.connect("shopBD.sqlite") as con:
					cur = con.cursor()
					cur.execute("DELETE FROM items WHERE id = ?", (int(getDataPayer[0]),))
				try:
					bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "✅ Благодарим вас за покупку. Ждём вас снова.\n`{0}`".format(sendBuy))
					if len(admin_id) > 1:
						for a in range(len(admin_id)):
							bot.send_message(admin_id[a], f"💰 Пользователь @{call.from_user.username} купил товар на сумму {getAmountQiwi[howChar]} руб")
					else:
						bot.send_message(admin_id[0], f"💰 Пользователь @{call.from_user.username} купил товар на сумму {getAmountQiwi[howChar]} руб")
				except requests.exceptions.ConnectionError:
					bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "✅ Благодарим вас за покупку. Ждём вас снова.\n`{0}`".format(sendBuy))
					if len(admin_id) > 1:
						for a in range(len(admin_id)):
							bot.send_message(admin_id[a], f"💰 Пользователь @{call.from_user.username} купил товар на сумму {getAmountQiwi[howChar]} руб")
					else:
						bot.send_message(admin_id[0], f"💰 Пользователь @{call.from_user.username} купил товар на сумму {getAmountQiwi[howChar]} руб")
			else:
				try:
					bot.send_message(call.from_user.id, "❗️ Ваша покупка не была найдена или была уже выдана.")
				except requests.exceptions.ConnectionError:
					bot.send_message(call.from_user.id, "❗️ Ваша покупка не была найдена или была уже выдана.")
		else:
			try:
				bot.send_message(call.from_user.id, "❗️ Пополнение не было найдено.\nПопробуйте чуть позже.")
			except requests.exceptions.ConnectionError:
				bot.send_message(call.from_user.id, "❗️ Пополнение не было найдено.\nПопробуйте чуть позже.")
####################################################################################################
#Добавление одиночных товаров
def add_item_name(message):
	global itemName
	itemName = message.text
	if itemName not in ignor_command:
		try:
			bot.send_message(message.from_user.id, "📘 Введите описание товара")
		except requests.exceptions.ConnectionError:
			bot.send_message(message.from_user.id, "📘 Введите описание товара")
		bot.register_next_step_handler(message, add_item_discription)

def add_item_discription(message):
	global itemDiscription
	itemDiscription = message.text
	if itemDiscription not in ignor_command:
		try:
			bot.send_message(message.from_user.id, "📘 Введите цену товара")
		except requests.exceptions.ConnectionError:
			bot.send_message(message.from_user.id, "📘 Введите цену товара")
		bot.register_next_step_handler(message, add_item_price)

def add_item_price(message):
	global itemPrice
	itemPrice = message.text
	if itemPrice not in ignor_command:
		try:
			bot.send_message(message.from_user.id, "📘 Введите данные товара")
		except requests.exceptions.ConnectionError:
			bot.send_message(message.from_user.id, "📘 Введите данные товара")
		bot.register_next_step_handler(message, add_item_data)

def add_item_data(message):
	global itemData
	itemData = message.text
	if itemData not in ignor_command:
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			cur.executemany("INSERT INTO items (name, description, price, data) VALUES (?, ?, ?, ?)", [(itemName, itemDiscription, itemPrice, itemData)])
		if con:
			con.close()
		try:
			bot.send_message(message.from_user.id, "📘 Товар был успешно добавлен")
		except requests.exceptions.ConnectionError:
			bot.send_message(message.from_user.id, "📘 Товар был успешно добавлен")
####################################################################################################
#Добавление массовых товаров
def add_items_name(message):
	global itemNames
	itemNames = message.text
	if itemNames not in ignor_command:
		try:
			bot.send_message(message.from_user.id, "📗 Введите описание товаров")
		except requests.exceptions.ConnectionError:
			bot.send_message(message.from_user.id, "📗 Введите описание товаров")
		bot.register_next_step_handler(message, add_items_discription)

def add_items_discription(message):
	global itemDiscriptions
	itemDiscriptions = message.text
	if itemDiscriptions not in ignor_command:
		try:
			bot.send_message(message.from_user.id, "📗 Введите цену товаров")
		except requests.exceptions.ConnectionError:
			bot.send_message(message.from_user.id, "📗 Введите цену товаров")
		bot.register_next_step_handler(message, add_items_price)

def add_items_price(message):
	global itemPrices
	itemPrices = message.text
	if itemPrices not in ignor_command:
		try:
			bot.send_message(message.from_user.id, "📗 Введите данные товаров в столбик. Пример:\n`login:password`\n`login:password`\n`login:password`", parse_mode = "MARKDOWN")
		except requests.exceptions.ConnectionError:
			bot.send_message(message.from_user.id, "📗 Введите данные товаров в столбик. Пример:\n`login:password`\n`login:password`\n`login:password`", parse_mode = "MARKDOWN")
		bot.register_next_step_handler(message, add_items_data)

def add_items_data(message):
	global itemDatas
	itemDatas = str(message.text)
	itemDatas = itemDatas.split("\n")
	counter	  = 0
	if itemDatas not in ignor_command:
		with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
			cur = con.cursor()
			for a in range(len(itemDatas)):
				cur.executemany("INSERT INTO items (name, description, price, data) VALUES (?, ?, ?, ?)", [(itemNames, itemDiscriptions, itemPrices, itemDatas[a])])
				counter += 1
		if con:
			con.close()
		try:
			bot.send_message(message.from_user.id, f"📘 {counter} товаров было успешно добавлено.")
		except requests.exceptions.ConnectionError:
			bot.send_message(message.from_user.id, f"📘 {counter} товаров было успешно добавлено.")
####################################################################################################
#Смена текста FAQ
def change_faq(message):
	with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
		cur = con.cursor()
		cur.execute("SELECT * FROM faq")
		while True:
			row = cur.fetchone()
			if row == None:
				break
			cur.execute("UPDATE faq SET infa = ? WHERE infa = ?", (message.text, row[0]))
	if con:
		con.close()
	try:
		bot.send_message(message.from_user.id, "🔘 FAQ былл обновлено")
	except requests.exceptions.ConnectionError:
		bot.send_message(message.from_user.id, "🔘 FAQ было обновлено")
####################################################################################################
#Смена киви данных
def change_qiwi_number(message):
	try:
		bot.send_message(message.from_user.id, "🥝 Введите токен QIWI API")
	except requests.exceptions.ConnectionError:
		bot.send_message(message.from_user.id, "🥝 Введите токен QIWI API")
	bot.register_next_step_handler(message, change_qiwi_token)
	global qiwi_login
	qiwi_login = message.text

def change_qiwi_token(message):
	try:
		bot.send_message(message.from_user.id, "🥝 Проверка введённых QIWI данных...")
	except requests.exceptions.ConnectionError:
		bot.send_message(message.from_user.id, "🥝 Проверка введённых QIWI данных...")
	time.sleep(2)
	try:
		request = requests.Session()
		request.headers["authorization"] = "Bearer " + message.text  
		parameters = {"rows": 5, "operation" : "IN"}
		selectQiwi = request.get("https://edge.qiwi.com/payment-history/v2/persons/" + qiwi_login + "/payments", params = parameters)
		if selectQiwi.status_code == 200:	
			with sqlite3.connect("shopBD.sqlite", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
				cur = con.cursor()
				cur.execute("SELECT * FROM qiwi")
				while True:
					row = cur.fetchone()
					if row == None:
						break
					cur.execute("UPDATE qiwi SET login = ?, token = ? WHERE login = ?", (qiwi_login, message.text, row[0]))
			if con:
				con.close()
			try:
				bot.delete_message(chat_id = message.chat.id, message_id = message.message_id + 1)
				bot.send_message(message.from_user.id, "✅ QIWI токен был успешно изменён")
			except requests.exceptions.ConnectionError:
				bot.delete_message(chat_id = message.chat.id, message_id = message.message_id + 1)
				bot.send_message(message.from_user.id, "✅ QIWI токен был успешно изменён")
		else:
			try:
				bot.delete_message(chat_id = message.chat.id, message_id = message.message_id + 1)
				bot.send_message(message.from_user.id, "❌ QIWI токен не прошёл проверку. Код ошибки: " + str(selectQiwi.status_code))
			except requests.exceptions.ConnectionError:
				bot.delete_message(chat_id = message.chat.id, message_id = message.message_id + 1)
				bot.send_message(message.from_user.id, "❌ QIWI токен не прошёл проверку. Код ошибки: " + str(selectQiwi.status_code))
	except:
		try:
			bot.delete_message(chat_id = message.chat.id, message_id = message.message_id + 1)
			bot.send_message(message.from_user.id, "❌ QIWI токен не прошёл проверку.\nВведённые вами данные не верны")
		except requests.exceptions.ConnectionError:		
			bot.delete_message(chat_id = message.chat.id, message_id = message.message_id + 1)
			bot.send_message(message.from_user.id, "❌ QIWI токен не прошёл проверку.\nВведённые вами данные не верны")
####################################################################################################
#Запуск бота с обработкой вылетов
if __name__ == "__main__":
	while True:
		try:
			print("BOT was started!")
			bot.polling(none_stop = True, interval = 0)
		except requests.exceptions.ConnectionError:
			print("Скрипт получил ошибку соединения 'ConnectionError'")
			time.sleep(10)
