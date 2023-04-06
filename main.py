import telebot
import webbrowser        #вроді для відкриття сайту
from telebot import types
import sqlite3    # база даних
import requests    #погода
import json
from currency_converter import CurrencyConverter  #конвертер валют

bot = telebot.TeleBot('6248161837:AAEC7LBPRd_tBcVHds5BstnmR4fh6cwRjHo')    #токен тг

currency = CurrencyConverter()    #об'єкт на основі класу для конвертера валют
name = ''         #глобальна змінна для бази даних
amount = 0
API = '29e1feb28c6343163dd0223b2084877d'    #для погоди, зв'язок з сайтом

@bot.message_handler(['convert'])       #конвертор валют
def convert(message):
    bot.send_message(message.chat.id, 'Привіт, введіть суму')
    bot.register_next_step_handler(message, summa)

def summa(message):
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Невірний формат, введіть число')
        bot.register_next_step_handler(message, summa)
        return

    if amount > 0:
        markup_convert = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('USD/EUR', callback_data='usd/eur')
        btn2 = types.InlineKeyboardButton('EUR/USD', callback_data='eur/usd')
        btn3 = types.InlineKeyboardButton('UAN/GBP', callback_data='usd/gbp')
        btn4 = types.InlineKeyboardButton('Інше значення', callback_data='else')
        markup_convert.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, 'Введіть пару валют', reply_markup=markup_convert)
    else:
        bot.send_message(message.chat.id, 'Невірне число, введыть ще раз')
        bot.register_next_step_handler(message, summa)


@bot.callback_query_handler(func=lambda call: True)
def callback_converter(call):
    if call.data != 'else':
        values = call.data.upper().split('/')
        res = currency.convert(amount, values[0], values[1])          #звернення до глобальної змінної і об'єкту на основі класу для конвертера валют
        bot.send_message(call.message.chat.id, f'Получається: {round(res, 2)}. Можете ввести суму ще раз')
        bot.register_next_step_handler(call.message, summa)
    else:
        bot.send_message(call.message.chat.id, 'Введіть пару значень через слеш')
        bot.register_next_step_handler(call.message, my_currency)

def my_currency(message):
    try:
        values = message.text.upper().split('/')
        res = currency.convert(amount, values[0], values[1])  # звернення до глобальної змінної і об'єкту на основі класу для конвертера валют
        bot.send_message(message.chat.id, f'Получається: {round(res, 2)}. Можете ввести суму ще раз')
        bot.register_next_step_handler(message, summa)
    except Exception:
        bot.send_message(message.chat.id, 'Щось не так, введіть значення заново')
        bot.register_next_step_handler(message, my_currency)




@bot.message_handler(commands=['sing'])     #реєстрація
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




@bot.callback_query_handler(func=lambda call: True)     #вивід зареєстрованих користувачів
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
    btn_1 = types.KeyboardButton('Чернівці')
    markup.row(btn_1)
    btn_2 = types.KeyboardButton('Шешори')
    btn_3 = types.KeyboardButton('Київ')
    markup.row(btn_2, btn_3)
    file = open('37897_elder_scrolls.jpg', 'rb')
    bot.send_photo(message.chat.id, file, reply_markup=markup)
    #bot.send_message(message.chat.id, 'Hi', reply_markup=markup)
    #bot.register_next_step_handler(message, on_click)

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