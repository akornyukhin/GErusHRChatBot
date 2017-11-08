import random
from datetime import datetime
import telebot
import tzlocal
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
engine = create_engine('postgres://baujmpgp:qiMRgtF0Dp_dUgQTATZqoS0xLgsqLEGE@horton.elephantsql.com:5432/baujmpgp')
 
from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)

local_timezone = tzlocal.get_localzone()
bot = telebot.TeleBot("477403081:AAGkP0dT1k4i4BjHZCjegkqrt-wcVOQ-Lso")
update = bot.get_updates()

user_dict = {}
number_of_users = 0

# ORM
Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    text = Column(String)

Base.metadata.create_all(engine)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global number_of_users
    bot.reply_to(message, "Hello, I am GE HR Chat bot. To see help type /help")
    bot.send_message(message.chat.id, str(message.from_user))

    user_dict['User {}'.format(random.random())] = message.from_user.id
    number_of_users += 1

    bot.send_message(428535905, str(user_dict))

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "I can answer most common HR questions. You ask wich one - my developer didn't tell me it yet :)")

@bot.message_handler(func=lambda message: True)
def echo_all(message):

    bot.reply_to(message, str(datetime.fromtimestamp(float(message.date), local_timezone).strftime("%d-%m-%Y %H:%M:%S")) + "    " + message.text)
    bot.send_message(428535905, message.text)

    message = Message(id=message.message_id, text=message.text)
    s = session()
    s.add(message)
    s.commit()
    s.query(Message).all()

bot.polling(none_stop=True)