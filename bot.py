import config as cfg
import tornado.web
import tornado.ioloop
import requests
import signal
import logging


URL = 'https://api.telegram.org/bot%s/' % cfg.BOT_TOKEN


def signal_term_handler(num, frame):
    print("STM called")
    logging.info("Bot stopped")
    exit(1)


logging.basicConfig(level=logging.INFO, filename=cfg.LogPath)


class Handler(tornado.web.RequestHandler):
    def post(self):
        try:
            logging.info("i'm in try")
            logging.info(f"Request: {self.request.body}")
            update = tornado.escape.json_decode(self.request.body)
            logging.info("Update: %s" % str(update))
        except Exception as exc:
            logging.error(str(exc))


api = requests.Session()
application = tornado.web.Application([
    (r"/", Handler),
])

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, signal_term_handler)
    try:
        set_hook = api.get(cfg.URL + "setwebhook?url=" + cfg.MyURL)
        if set_hook.status_code != 200:
            print(set_hook.status_code, set_hook.text, sep='\n')
            print("Cannot set webhook")
            exit(1)
        application.listen(8888)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        signal_term_handler(signal.SIGTERM, None)