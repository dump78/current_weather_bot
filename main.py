import telebot
from telebot import types
import requests
import json
from config import TOKEN, HEADERS, CONDITIONS
from messages import ask_geo_message, error_geo_message, error_data_message


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start_get_weather(message):
    hello_message = 'Привет, {0}!\n\nЧтобы узнать погоду, введите команду /weather'.format(message.from_user.first_name)
    bot.send_message(message.chat.id, text=hello_message)


@bot.message_handler(commands=["weather"])
def get_weather(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Узнать погоду!", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, ask_geo_message, reply_markup=keyboard)


@bot.message_handler(content_types=["location"])
def send_weather(message):
    if message.location is not None:
        latitude = message.location.latitude
        longitude = message.location.longitude
        url = "https://api.weather.yandex.ru/v2/informers?lat={0}&lon={1}&lang=ru_RU".format(latitude, longitude)
    else:
        bot.send_message(message.chat.id, error_geo_message)

    r = requests.get(url=url, headers=HEADERS)
    if r.status_code == 200:
        data = json.loads(r.text)
        fact = data["fact"]
        bot.send_message(message.chat.id, text='Погода в вашем населенном пункте {0}°, ощущается как {1}°.'
                                               '\nСейчас на улице {2}.'
                                               '\nСкорость ветра достигает {3} м/c, а его порывов - {4} м/с. '
                                               '\nДавление {5} мм рт. ст.\nУдачного дня! \U0001F60A'.format(fact["temp"],
                                                                                                            fact["feels_like"],
                                                                                                            CONDITIONS.get(fact["condition"]),
                                                                                                            fact["wind_speed"],
                                                                                                            fact["wind_gust"],
                                                                                                            fact["pressure_mm"]))
    else:
        bot.send_message(message.chat.id, error_data_message)


bot.polling(none_stop=True)
