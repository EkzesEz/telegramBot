import logging

import requests
import tornado.web

import config as cfg

weather_url = 'https://api.openweathermap.org/data/2.5/'


def get_weather(city_name, api_key=cfg.weather_api_key):
    try:
        response = requests.get(weather_url + 'weather',
                                params={'q': f"{city_name}", 'appid': api_key})
    except:
        return 0
    return response.json()


def weather(chat, city):
    data = get_weather(city)
    cod = data['cod']
    if cod != 200:
        logging.error(f"cod = {cod}, {type(cod)}")
        match cod:
            case '404':
                return "Город не найден. Попробуйте еще раз"
            case _:
                return f"Произошла ошибка {cod}. Попробуйте еще раз"
    main_data = data['weather'][0]['main']
    temp = data['main']['temp'] - 273.1
    temp_f = 1.8 * temp + 32
    newmsg = f"{main_data}, {round(temp,1)}\N{DEGREE SIGN}C ({round(temp_f,1)}\N{DEGREE SIGN}F)"
    logging.info(f"returning message{newmsg}")
    return newmsg
