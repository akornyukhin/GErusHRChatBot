import telebot
import os
import logging
import json
import pandas as pd
from flask import Flask, request
from telebot import types

#Constrants
UPLOAD_FOLDER = './static/'
API_TOKEN = os.getenv('TOKEN')
WEBHOOK_HOST = json.loads(os.getenv('VCAP_APPLICATION'))['application_uris'][0]
WEBHOOK_URL_BASE = "https://{}".format(WEBHOOK_HOST)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)

#Bot init
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

THREADED = True
bot = telebot.TeleBot(API_TOKEN, threaded=THREADED)
app = Flask(__name__)


# Getting data from DB
df = pd.read_excel('./static/hrdata.xlsx', index_col=0)
list_of_values = df.loc[df['node_id'] == 1, ['id','body']].to_csv(sep="\t", header=False)

# Setting the webhook
@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)
    return "!", 200

# Updates processing
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

# Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello, I am GE HR Chat bot. To see help type /help. To ask the question type /ask.")

# Help command
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "I can answer most common HR questions. Type /ask to begin.")

# Ask command
@bot.message_handler(commands=['ask'])
@bot.message_handler(regexp = '^Ask another question$')
def send_ask(message):
    bot.send_message(message.chat.id, "Chose what you want to know: \n" + list_of_values,
    reply_markup = buttons(df.loc[df.node_id == 1].index.astype('str')))

# Handling questions
@bot.message_handler(regexp = '\d')
def send_answer(message):
    answer_id = int(message.text)
    ref_node_id = df.get_value(answer_id,'ref_node_id')

    flag = False
    if len(list(df.loc[df['node_id'] == ref_node_id, 'ref_node_id'])) == 1:
        flag = True

    result = df.loc[df['node_id'] == ref_node_id, ['body']].reset_index().to_csv(sep="\t", header=False, index=False)
    markup = buttons(df.loc[df['node_id'] == ref_node_id].index.astype('str'), end=flag)
    bot.reply_to(message, result, reply_markup=markup)

# Echo questions
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, "To see help type /help. To ask the question type /ask.")

#Buttons markup
def buttons(list, end=False):
    markup = types.ReplyKeyboardMarkup(selective=True)
    if end == True:
        markup.row(types.KeyboardButton('Ask another question'))
    else:
        for item in list:
            markup.row(types.KeyboardButton(item))
    return markup

if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=int(os.getenv('PORT')))