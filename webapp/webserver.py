
import json
import locale
import os
from datetime import datetime
import sys
import bleach
import web
from twitch import TwitchClient
import markdown

from urllib import unquote
import posixpath
import urllib
import stockstream
import tradingview_api
import robinhood
import scrub
from gunicorn.app.base import BaseApplication
import multiprocessing

import gunicorn.app.base

from gunicorn.six import iteritems

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

t_globals = dict(datestr=web.datestr,
                 round=round,
                 stockstream=stockstream,
                 robinhood=robinhood,
                 tradingview_api=tradingview_api,
                 datetime=datetime,
                 scrub=scrub,
                 locale=locale,
                 json=json,
                 str=str,
                 bleach=bleach)

urls = (
    '/robots.txt', 'Robots',
    '/info/*(.+)', 'Info',
    '/symbol/*(.+)', 'Symbol',
    '/portfolio*(.+)', 'Portfolio',
    '/player/*(.+)', 'Player',
    '/*(.+)', 'Index'
)


def notfound():
    return render.pages.error()


class StockStreamWebApp(web.application):
    def run(self, *middleware):
        port = 8080
        if 'PORT' in os.environ:
            port = os.environ['PORT']
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

render = web.template.render('templates/', globals=t_globals)
render._keywords['globals']['render'] = render


class Robots:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    def GET(self):
        return "User-agent: *\nAllow: /"


class Info:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    def GET(self, page):
        try:
            markdown_converter = markdown.Markdown(output_format='html4')
            info_file = 'markdown/{}.markdown'.format(page)
            info_text = open(info_file, 'r').read()
            content = markdown_converter.convert(info_text)

            return render.pages.info(content)
        except Exception as ex:
            return notfound()


class Symbol:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    def GET(self, symbol):
        try:
            render._keywords['globals']['model'] = {}

            symbol = symbol.upper()

            return render.pages.symbol(symbol)
        except Exception as ex:
            return notfound()


class Player:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    def GET(self, scoped_username):
        try:
            name = scoped_username.split(":")[1]
            client = TwitchClient(client_id='ohlre6lyirmibqf5jhxz8taxnnc3m6')
            users = client.users.translate_usernames_to_ids([name])
            channel = client.channels.get_by_id(users[0]['id'])

            render._keywords['globals']['model'] = {}

            return render.pages.player(scoped_username, channel)
        except Exception as ex:
            return notfound()


class Portfolio:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    def GET(self, url):

        render._keywords['globals']['model'] = {}

        return render.pages.portfolio()


class Index:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    def GET(self, url):
        return render.pages.index()


class StaticMiddleware:
    """WSGI middleware for serving static files."""

    def __init__(self, app, prefix='/static/'):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        path = self.normpath(path)

        if path.startswith(self.prefix):
            return web.httpserver.StaticApp(environ, start_response)
        else:
            return self.app(environ, start_response)

    def normpath(self, path):
        path2 = posixpath.normpath(unquote(path))
        if path.endswith("/"):
            path2 += "/"
        return path2

class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


app = StockStreamWebApp(urls, globals())

app.daemon = True
#app.notfound = notfound
app.notfound = web.debugerror

wsgi = app.wsgifunc()
wsgi = StaticMiddleware(wsgi)


if __name__ == '__main__':
    port = os.environ['PORT']

    options = {
        'bind': '%s:%s' % ('0.0.0.0', port),
        'workers': 15,
    }
    StandaloneApplication(wsgi, options).run()
