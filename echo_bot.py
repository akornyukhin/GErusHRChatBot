import telebot

bot = telebot.TeleBot("477403081:AAGkP0dT1k4i4BjHZCjegkqrt-wcVOQ-Lso")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello, I am GE HR Chat bot. How can I help you?")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "I can answer most common HR questions. You ask wich one - my developer didn't tell me it yet :)")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	# bot.reply_to(message, message.text)
    bot.send_message(message.chat.id, str(message.date) + "    " + message.text)

bot.polling()