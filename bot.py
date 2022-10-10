import config as cfg
import tornado.web
import tornado.ioloop
import requests
import signal
import logging


URL = 'https://api.telegram.org/bot%s/' % cfg.BOT_TOKEN


class Handler(tornado.web.RequestHandler):
    def post(self):
        try:
            logging.info("i'm in try")
            request = tornado.escape.json_decode(self.request.body)
            logging.info("Request: %s" % str(request))
            message = request['message']
            text = message.get('text')
            chat_id = message['chat']['id']
            if 'entities' in message:
                if message['entities'][0]['type'] == 'bot_command':
                    if reply(chat_id, f"You sent command: {text}\nThank you!"):
                        logging.info("Message sent!")
                    else:
                        logging.info("Cant send msg")
            else:
                reply(chat_id, f"You sent text: {text}\nThank you!")
        except Exception as exc:
            logging.error(str(exc))


api = requests.Session()
application = tornado.web.Application([
    (r"/", Handler),
])


def signal_term_handler(num, frame):
    print("STM called")
    logging.info("Bot stopped")
    exit(1)


def reply(chat_id, response):
    logging.info("I'm in reply. Trying to send %s" % response)
    if api.post(URL + 'sendMessage', data={'chat_id': chat_id, 'text': response}):
        return 1
    return 0


logging.basicConfig(level=logging.INFO, filename=cfg.LogPath, format="%(asctime)s %(levelname)s %(message)s")





if __name__ == '__main__':
    signal.signal(signal.SIGTERM, signal_term_handler)
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