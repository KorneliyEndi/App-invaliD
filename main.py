import telebot
import webbrowser
from telebot import types
import sqlite3
import requests
import json

bot = telebot.TeleBot('6248161837:AAEC7LBPRd_tBcVHds5BstnmR4fh6cwRjHo')
name = ''
API = '29e1feb28c6343163dd0223b2084877d'











@bot.message_handler(commands=['sing'])
def sing(message):
    conn = sqlite3.connect('baza_danih.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50))')
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Йоу, введіть свій логін')
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, 'введіть свій пароль')
    bot.register_next_step_handler(message, user_pass)

def user_pass(message):
    password = message.text.strip()

    conn = sqlite3.connect('baza_danih.sql')
    cur = conn.cursor()

    cur.execute("INSERT INTO users (name, pass) VALUES ('%s', '%s')" % (name, password))
    conn.commit()
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Список кор', callback_data='users'))
    bot.send_message(message.chat.id, 'Користувач зареєстрований', reply_markup=markup)
    #bot.register_next_step_handler(message, user_pass)




@bot.callback_query_handler(func=lambda call: True)
def callbak(call):
    conn = sqlite3.connect('baza_danih.sql')
    cur = conn.cursor()

    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f"Ім'я: {el[1]}, пароль: {el[2]}\n"
    cur.close()
    conn.close()

    bot.send_message(call.message.chat.id, info)


@bot.message_handler(commands=['buttons'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    btn_1 = types.KeyboardButton('Кнопка для дій')
    markup.row(btn_1)
    btn_2 = types.KeyboardButton('Видалити фото')
    btn_3 = types.KeyboardButton('Змінити текст')
    markup.row(btn_2, btn_3)
    file = open('37897_elder_scrolls.jpg', 'rb')
    bot.send_photo(message.chat.id, file, reply_markup=markup)
    #bot.send_message(message.chat.id, 'Hi', reply_markup=markup)
    bot.register_next_step_handler(message, on_click)

#def on_click(message):
 #   if message.text == 'Кнопка для дій':
  #      bot.send_message(message.chat.id, 'Єбать, працює')
   # elif message.text == 'Видалити фото':
    #    bot.send_message(message.chat.id, 'suk')

@bot.message_handler(commands=['resume'])                                 #функція для відкриття сайту
def site(message):
    webbrowser.open('https://adorable-travesseiro-7a8c6a.netlify.app')

@bot.message_handler(commands=['start'])                       #функція для обробки конкретних команд
def main(message):
    bot.send_message(message.chat.id, f'Hello, {message.from_user.first_name} {message.from_user.last_name}')

@bot.message_handler(commands=['help'])                                  #така ж функція для відправки повідомлень але форматованих в html
def main(message):
    bot.send_message(message.chat.id, '<b>Help</b> <em><u>information</u></em>', parse_mode='html')

@bot.message_handler(commands=['about_me'])
def main(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name} {message.from_user.last_name}, \nID:{message.from_user.id}')

#@bot.message_handler()                                           #функція для роботи з текстом
#def info(message):
#    if message.text.lower() == 'слава україні':
#        bot.send_message(message.chat.id, 'Героям слава')
#    elif message.text.lower() == 'id':
#        bot.reply_to(message, f'ID: {message.from_user.id}')      #відповідь на попереднє повідомлення




@bot.message_handler(commands=['pogoda'])
def pogoda(message):
    bot.send_message(message.chat.id, 'Привіт, введіть назву міста')

@bot.message_handler(content_types=['text'])
def get_weather(message):
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = data["main"]["temp"]
        bot.reply_to(message, f'Зараз погода: {temp}')

        image = '85479c35384235964bb5d2db947db1ee29173d3c.jpeg' if temp > 5.0 else 'depositphotos_214593002-stock-illustration-cloudy-icon-vector-isolated-on.jpg'
        file = open(image, 'rb')
        bot.send_photo(message.chat.id, file)
    else:
        bot.reply_to(message, 'Місто вказано не вірно')



bot.polling(none_stop=True)