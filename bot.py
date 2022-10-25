import logging
import signal

import requests
import tornado.ioloop
import tornado.web

import config as cfg
from methods import weather

URL = 'https://api.telegram.org/bot%s/' % cfg.BOT_TOKEN


logging.basicConfig(level=logging.INFO, filename=cfg.LogPath,
                    format="%(asctime)s %(levelname)s %(message)s")


class Handler(tornado.web.RequestHandler):
    def post(self):
        try:
            logging.info("i'm in try")
            request = tornado.escape.json_decode(self.request.body)
            logging.info("Request: %s" % str(request))
            message = request['message']
            text = message.get('text')
            chat_id = message['chat']['id']
            if chat_id in to_ans['weather']:
                logging.info(
                    f"trying to post weather in chat id = {chat_id}, city = {text}")
                to_ans['weather'].pop(to_ans['weather'].index(chat_id))
                signal.alarm(3)
                reply(chat_id, weather(text))
                signal.alarm(0)
            else:
                if 'entities' in message:
                    if message['entities'][0]['type'] == 'bot_command':
                        response = commands.get(text)
                        reply(chat_id, response.replace('\\n', '\n'))
                        match text:
                            case '/weather':
                                to_ans['weather'].append(chat_id)
                                logging.info(
                                    f"In case weather, to_ans = {to_ans}")
                else:
                    reply(chat_id, f"You sent text: {text}\nThank you!")
        except TimeoutError as exc:
            reply(chat_id, "Weather server is unreachable.")
            logging.error(exc)
        except Exception as exc:
            logging.error(str(exc))


api = requests.Session()
application = tornado.web.Application([
    (r"/", Handler),
])


def signal_term_handler(signum, frame):
    logging.info("Bot stopped")
    exit(1)


def signal_alrm_handler(signum, frame):
    logging.error("SAH called")
    raise TimeoutError("Weather Api didn't answer in 3 sec")


def init_cmd(dict):
    cmd_file = open(cfg.commands_path)
    for line in cmd_file:
        cmd, resp = line.split(maxsplit=1)
        dict[cmd] = resp
    cmd_file.close()


def reply(chat_id, response):
    logging.info("I'm in reply. Trying to send %s" % response)
    if api.post(URL + 'sendMessage', data={'chat_id': chat_id, 'text': response}):
        return 1
    return 0


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, signal_term_handler)
    signal.signal(signal.SIGALRM, signal_alrm_handler)

    commands = {}

    init_cmd(commands)

    to_ans = {'weather': []}

    try:
        set_hook = api.get(URL + "setwebhook?url=" + cfg.MyURL)
        if set_hook.status_code != 200:
            print(set_hook.status_code, set_hook.text, sep='\n')
            logging.error("Webhook error")
            exit(1)
        application.listen(8888)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        signal_term_handler(signal.SIGTERM, None)
