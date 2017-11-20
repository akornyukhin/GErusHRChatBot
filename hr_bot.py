import random
from datetime import datetime
import telebot
from telebot import types
import os
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import create_engine

engine = create_engine(os.getenv('CSTRING'))
 
from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)

import pandas as pd

# Getting data from DB
df = pd.read_sql('hrdata', engine, index_col='id')
list_of_values = df.loc[df.node_id == 1, ['id','body']].to_csv(sep="\t", header=False)

# Bot init
bot = telebot.TeleBot(os.getenv('TOKEN'))

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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello, I am GE HR Chat bot. To see help type /help. To ask the question type /ask.")
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
    bot.reply_to(message, "I can answer most common HR questions. Type /ask to begin.")

    user_id = message.from_user.id
    message = Message(id=message.message_id, text=message.text)
    s = session()
    s.add(message)
    s.query(Message).all()
    s.query(User).filter(User.id == user_id).update({User.number_of_msg: User.number_of_msg + 1}, synchronize_session = False)
    s.commit()

@bot.message_handler(commands=['ask'])
@bot.message_handler(regexp = '^Ask another question$')
def send_ask(message):
    bot.send_message(message.chat.id, "Chose what you want to know: \n" + list_of_values,
    reply_markup = buttons(df.loc[df.node_id == 1].index.astype('str'))
    )

    user_id = message.from_user.id
    message = Message(id=message.message_id, text=message.text)
    s = session()
    s.add(message)
    s.query(Message).all()
    s.query(User).filter(User.id == user_id).update({User.number_of_msg: User.number_of_msg + 1}, synchronize_session = False)
    s.commit()

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

    user_id = message.from_user.id
    message = Message(id=message.message_id, text=message.text)
    
    s = session()
    s.add(message)
    s.query(Message).all()
    s.query(User).filter(User.id == user_id).update({User.number_of_msg: User.number_of_msg + 1}, synchronize_session = False)
    s.commit()


@bot.message_handler(func=lambda message: True)
def echo_all(message): 
    user_id = message.from_user.id
    message = Message(id=message.message_id, text=message.text)
    
    bot.reply_to(message, 'To ask a question type /ask')

    s = session()
    s.add(message)
    s.query(Message).all()
    s.query(User).filter(User.id == user_id).update({User.number_of_msg: User.number_of_msg + 1}, synchronize_session = False)
    s.commit()

def buttons(list, end=False):
    markup = types.ReplyKeyboardMarkup(selective=True)
    if end == True:
        markup.row(types.KeyboardButton('Ask another question'))
    else: 
        for item in list:
            markup.row(types.KeyboardButton(item))
    return markup

bot.polling(none_stop=True)