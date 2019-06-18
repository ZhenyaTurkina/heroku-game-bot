#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pymorphy2
import numpy as np
import pickle
import telebot
import os
import re

morph = pymorphy2.MorphAnalyzer()

with open('games_precalc.pkl', 'rb') as f:
    game_set = pickle.load(f)

def get_tags(word):
    parse_word = morph.parse(word)[0]
    pos = parse_word.tag.POS
    animacy = parse_word.tag.animacy
    aspect = parse_word.tag.aspect
    case = parse_word.tag.case
    gender = parse_word.tag.gender
    involvement = parse_word.tag.involvement
    mood = parse_word.tag.mood
    number = parse_word.tag.number
    person = parse_word.tag.person
    tense = parse_word.tag.tense
    transitivity = parse_word.tag.transitivity
    voice = parse_word.tag.voice


    tags = set()
    for tag in [pos, animacy, aspect, case,
               gender, involvement, mood, number,
               person, tense, transitivity, voice]:
        if tag is not None:
            tags.add(str(tag))
    return tags



# In[4]:


def replace_words(sentens):
    words = re.findall(r"[А-Яа-я]+", sentens)
    word_2_replace_count = max(1, int(len(words) * 0.1))
    
    index = np.random.choice(range(len(words)), size=word_2_replace_count, replace=False)
    
    for i in index:
        parse_word = morph.parse(words[i])[0]

        pos = str(parse_word.tag.POS)
        tags = get_tags(word)

        rnd_index  = np.random.choice(range(len(pos_map[pos])),  size=len(pos_map[pos]), replace=False)
        new_word = None
        for ind in  rnd_index:
            rnd_word = pos_map[pos][ind]
            parse_rnd_word = morph.parse(rnd_word)[0]
            new_word = parse_rnd_word.inflect(tags)
            
            if new_word is not None:
                break
        
        if new_word is  None:
            continue
            
        sentens = sentens.replace(words[i], new_word.word)
    
    return sentens


# In[5]:


def  get_sample(sentenses, count ):
    

    indexes = np.random.choice(range(len(sentenses)), size=count, replace=False)

    sample = np.array(final_sentenses)[indexes]

    final_sentens = []
    for i in range(count //2):
        cur_sentens = sample[i].strip()

        final_sentens.append((replace_words(cur_sentens), True))

    for i in range(count //  2, count):
        final_sentens.append((sample[i].strip(), False))
    
    final_sentens = np.array(final_sentens)
    index_shuffle = np.random.choice(range(count), size=count, replace=False)
    return final_sentens[index_shuffle]


from collections import defaultdict
START, FIRST_PLAY, PLAY, END = range(4)


# In[65]:


TOKEN = "795366462:AAEgV7kG6k0B1hPG-0CWJISTL12itERt16Q"
WEBHOOK_HOST = 'testbotbottest.herokuapp.com'
WEBHOOK_PORT = '443'


# In[66]:


WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(TOKEN)


# In[78]:

import flask
from flask import Flask
# telebot.apihelper.proxy = {'https': 'socks5h://geek:socks@t.geekclass.ru:7777'} #задаем прокси
bot = telebot.TeleBot(TOKEN, threaded=False)  # бесплатный аккаунт pythonanywhere запрещает работу с несколькими тредами

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)


# In[79]:


import telebot
from telebot.types  import ReplyKeyboardMarkup, KeyboardButton

USER_STATE = defaultdict(lambda: START)
USER_GAME = defaultdict(lambda: np.random.choice(range(500)))
USER_STATS = defaultdict(lambda: {"correct": 0, "wrong": 0})


def make_game_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2)
    
    buttons = [KeyboardButton("Робот!"), KeyboardButton("Толстой!")]
    keyboard.add(*buttons)
    
    return  keyboard


@bot.message_handler(func = lambda message: USER_STATE[message.chat.id] == START)
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    print('start')
    message_text  = "Привет!\n"                     " Это бот-игра."                     "Твоя задача очень просто, нужно угадать "                     "сгенерированное это предложение или оригинальное."                     "Начнем?"
    
    USER_STATE[message.chat.id] = FIRST_PLAY
    bot.send_message(chat_id=message.chat.id, text=message_text)

@bot.message_handler(commands=['close', 'exit'])
def handle_exit(message):
    print('exit handle')
    message_text = ":(\n" \
                   "Буду тебя ждать :3 \n" \
                   "Чтобы вернуться и начать новую игру, и введи любое сообщение"
    
    chat_id  = message.chat.id
    USER_STATE[message.chat.id] = START
    bot.send_message(chat_id=chat_id,  text=message_text)

@bot.message_handler(func  = lambda message: USER_STATE[message.chat.id] == FIRST_PLAY)
def handle_first_step(message):
    USER_GAME[message.chat.id] = np.random.choice(range(500))
    bot.send_message(chat_id=message.chat.id, text=game_set[USER_GAME[message.chat.id]][0],  reply_markup=make_game_keyboard())
    USER_STATE[message.chat.id] = PLAY
    USER_STATS[message.chat.id] = {"correct": 0, "wrong": 0}

    
@bot.message_handler(func  = lambda message:  USER_STATE[message.chat.id] == PLAY)
def handle_game(message):    
    answer = message.text == "Робот!"
    chat_id = message.chat.id
    
    index = USER_STATS[message.chat.id]["correct"] + USER_STATS[message.chat.id]["wrong"]
    
    
    correct_answer = game_set[USER_GAME[message.chat.id]][index][1] == 'True'
    
    if bool(correct_answer) == bool(answer):
        message =  "Правильно!"
        USER_STATS[chat_id]["correct"] += 1
    else:
        message = "Неправильно :("
        USER_STATS[chat_id]["wrong"] += 1
    
    bot.send_message(chat_id=chat_id, text=message)
    
    
    if index + 1 >= 10:
        message = "Конец игры!"
        USER_STATE[chat_id] = END
        
        keyboard = ReplyKeyboardMarkup(row_width=1)
        keyboard.add(KeyboardButton("Результат"))
    else:
        keyboard = make_game_keyboard()
        message = game_set[USER_GAME[chat_id]][index +  1]
    
    
    bot.send_message(chat_id=chat_id, text=message, reply_markup=keyboard)
    

@bot.message_handler(func  = lambda message:  USER_STATE[message.chat.id] == END)
def handle_end(message):
    chat_id = message.chat.id
    
    correct = USER_STATS[chat_id]["correct"]
    wrong = USER_STATS[chat_id]["wrong"]
    
    message_text = f"Результат: \n"                    f"Правильные ответы: {correct}\n"                    f"Неправильные ответы: {wrong}"
    
    keyboard = ReplyKeyboardMarkup(row_width=1)
    keyboard.add(KeyboardButton("Еще раз!"))
    
    USER_STATE[chat_id] = FIRST_PLAY
    
    bot.send_message(chat_id=chat_id,  text=message_text, reply_markup=keyboard)


app = Flask(__name__)

@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'ok'

@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    
    
if __name__ == '__main__':
    print("yo")
    app.debug = False
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    print("run")
else:
    flask.abort(403)

