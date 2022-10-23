import requests
import config as cfg
import tornado.web
import logging


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
    if data['cod'] != 200:
        return "Произошла ошибка. Попробуйте еще раз"
    main_data = data['weather'][0]['main']
    temp = data['main']['temp'] - 273.1
    temp_f = 1.8 * temp + 32
    newmsg = f"{main_data}, {round(temp,1)}\N{DEGREE SIGN}C ({round(temp_f,1)}\N{DEGREE SIGN}F)"
    logging.info(f"returning message{newmsg}")
    return newmsg
