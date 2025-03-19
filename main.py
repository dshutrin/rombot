import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from database import Base
from pprint import pprint


bot = telebot.TeleBot(token=token)
base = Base()

admin_main_key = InlineKeyboardMarkup()
admin_main_key.row(
	InlineKeyboardButton(text='Добавить шаблон', callback_data='add_template'), InlineKeyboardButton(text='Удалить шаблон', callback_data='rm_template')
)
admin_main_key.row(
	InlineKeyboardButton(text='Проверить код', callback_data='check_code')
)


@bot.message_handler(commands=['start'])
def start(message):

	if base.is_admin(message.chat.id):
		bot.send_message(message.chat.id, 'Выберите действие', reply_markup=admin_main_key)
	else:
		status = bot.get_chat_member(chat_id, message.chat.id)
		if status.status in ('member', 'administrator'):
			bot.send_message(message.chat.id, 'Привет!\nПришли мне код =)')
		else:
			bot.send_message(
				message.chat.id,
				'Для использования бота вы должны вступить в наш Telegram канал.\nhttps://t.me/romatestchannel_dimpy\nВступите и напишите нам /start'
			)


@bot.message_handler(content_types=['text'])
def message_handler(message):

	if base.is_admin(message.chat.id):

		if base.get_mode(message.chat.id) == 'add_phrase':
			base.set_phrase(message.chat.id, message.text)
			bot.send_message(message.chat.id, 'Теперь пришли ответ на эту фразу')
			base.change_mode(message.chat.id, 'add_answer')

		elif base.get_mode(message.chat.id) == 'add_answer':
			query = base.get_query(message.chat.id)
			answer = message.text

			status = base.add_task(query, answer)

			if status == 'Успех':
				bot.send_message(message.chat.id, f'{status}', reply_markup=admin_main_key)
			elif status == 'Такая фраза уже существует':
				bot.send_message(message.chat.id, f'Ошибка!\n{status}', reply_markup=admin_main_key)

			base.change_mode(message.chat.id, 'start')

		elif base.get_mode(message.chat.id) == 'get_check':
			code = message.text
			ans = base.get_answer(code)

			bot.send_message(message.chat.id, f'Ответ: "{ans}"', reply_markup=admin_main_key)
			base.change_mode(message.chat.id, 'start')

		elif base.get_mode(message.chat.id) == 'get_rm':
			ans = base.rm_code(message.text)

			if ans == 'Успех':
				bot.send_message(message.chat.id, 'Код удалён!', reply_markup=admin_main_key)
				base.change_mode(message.chat.id, 'start')
			elif ans == 'Не найден':
				bot.send_message(message.chat.id, 'Код не найден!', reply_markup=admin_main_key)
				base.change_mode(message.chat.id, 'start')

	else:
		if bot.get_chat_member(chat_id, message.chat.id).status == 'member':
			ans = base.get_answer(message.text)
			if ans:
				bot.send_message(message.chat.id, f'Ответ:\n\n{ans}')
		else:
			bot.send_message(
				message.chat.id,
				'Для использования бота вы должны вступить в наш Telegram канал.\nhttps://t.me/romatestchannel_dimpy\nВступите и напишите нам /start'
			)


@bot.callback_query_handler(func=lambda x: x)
def callback_handler(message):
	if base.is_admin(message.from_user.id):

		if message.data == 'add_template':

			bot.answer_callback_query(message.id)
			bot.send_message(message.message.chat.id, 'Пришли мне ключевую фразу')
			base.change_mode(message.message.chat.id, 'add_phrase')

		elif message.data == 'rm_template':
			bot.answer_callback_query(message.id)
			bot.send_message(message.message.chat.id, 'Пришли мне ключевую фразу и я удалю её из базы')
			base.change_mode(message.message.chat.id, 'get_rm')

		elif message.data == 'check_code':
			bot.answer_callback_query(message.id)
			bot.send_message(message.message.chat.id, 'Пришли мне ключевую фразу')
			base.change_mode(message.message.chat.id, 'get_check')

	else:
		bot.answer_callback_query(message.message.chat.id, 'Как ты сюда попал?...')


bot.polling(none_stop=True)
