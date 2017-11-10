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

import pandas as pd

bot = telebot.TeleBot("477403081:AAGkP0dT1k4i4BjHZCjegkqrt-wcVOQ-Lso")

# ORM
Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    text = Column(String)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True, index=True)
    number_of_msg = Column(Integer)

class HRdata(Base):
    __tablename__ = 'hrdata'
    id = Column(Integer, primary_key = True)
    node_id = Column(Integer)
    body = Column(String)
    ref_node_id = Column(Integer)

Base.metadata.create_all(engine)

df = pd.read_sql('hrdata', engine, index_col = 'id')
df['id'] = df.index.values

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello, I am GE HR Chat bot. To see help type /help")
    bot.send_message(message.chat.id, str(message.from_user))

    user = User(id = message.from_user.id, number_of_msg = 0)
    s = session() 

    try:
        s.add(user)
        s.query(User).all()
        s.commit()
    except:
        s.rollback()

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "I can answer most common HR questions. You ask wich one - my developer didn't tell me it yet :)")

@bot.message_handler(commands=['ask'])
def send_ask(message):
    bot.send_message(message.chat.id, 'Chose what you want to know: \n' + df.loc[df['node_id'] == 1,'body'])

@bot.message_handler(regexp = '\d')
def send_answer(message):
    answer_id = int(message.text)
    ref_node_id = df.get_value(answer_id,'ref_node_id')
    
    # 
    # Необходимо сделать обертку для id в str
    # 
    result = df.loc[df['node_id'] == ref_node_id, ['id','body']].values
    result = "\n".join([" ".join(row) for row in result])

    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, str(message.date) + "    " + message.text)
    bot.send_message(428535905, message.text + "    "  + str(message.from_user.id))
    
    user_id = message.from_user.id
    message = Message(id=message.message_id, text=message.text)
    
    s = session()
    s.add(message)
    s.query(Message).all()
    s.query(User).filter(User.id == user_id).update({User.number_of_msg: User.number_of_msg + 1}, synchronize_session = False)
    s.commit()



bot.polling(none_stop=True)