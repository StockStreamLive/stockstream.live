
import json
import locale
import os
from datetime import datetime
import bleach
import web
import markdown

from urllib import unquote
import posixpath
import stockstream
import tradingview_api
import robinhood
import scrub
from gunicorn.app.base import BaseApplication
import twitch_api
from expiringdict import ExpiringDict

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
    '/charts*(.+)', 'Charts',
    '/*(.+)', 'Index'
)


model_cache = ExpiringDict(max_len=1, max_age_seconds=60)
def load_display_model():
    model = model_cache['model'] if 'model' in model_cache else None

    if not model:
        model = {
                'portfolio_values': stockstream.api.get_portfolio_values(),
                'portfolio_stats': stockstream.portfolio.compute_portfolio_statistics(),
                'order_stats': stockstream.api.get_order_stats(),
                'top_players_list': stockstream.players.get_top_players_list(),
                'orders': stockstream.api.get_orders_today(),
            }

    model_cache['model'] = model

    return model


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
        markdown_converter = markdown.Markdown(output_format='html4')
        info_file = 'markdown/{}.markdown'.format(page)
        info_text = open(info_file, 'r').read()
        content = markdown_converter.convert(info_text)

        return render.pages.info(content)


class Charts:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    def GET(self, url):
        render._keywords['globals']['model'] = load_display_model()

        return render.pages.charts()


class Symbol:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    def GET(self, symbol):
        symbol = symbol.upper()

        instrument = robinhood.api.get_instrument_for_symbol(symbol)
        portfolio = stockstream.api.get_current_portfolio()
        positions = stockstream.api.get_positions_by_symbol(symbol)
        asset_map = stockstream.portfolio.get_symbol_to_asset(portfolio)
        portfolio_value = stockstream.portfolio.compute_value(portfolio)
        quote = robinhood.api.get_quote(symbol)

        asset_stats = {}
        if symbol in asset_map:
            asset_stats = stockstream.portfolio.compute_asset_stats(asset_map[symbol], portfolio_value, quote)

        render._keywords['globals']['model'] = {
            'orders': stockstream.api.get_orders_by_symbol(symbol),
            'fundamentals': robinhood.api.get_fundamentals(symbol),
            'market': tradingview_api.get_market_for_instrument(instrument),
            'stats_for_symbol': stockstream.metrics.compute_stats_for_symbol(symbol),
            'asset_map': asset_map,
            'asset_stats': asset_stats,

            'portfolio': portfolio,
            'positions': positions,
            'instrument': instrument,

            'symbol_profile': stockstream.positions.assemble_positions(positions),
        }

        return render.pages.symbol(symbol)


class Player:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    def GET(self, scoped_username):
        scoped_username = scoped_username.lower()
        name = scoped_username.split(":")[1]
        channel = twitch_api.get_channel_for_user(name)

        if channel['logo'] is None:
            channel['logo'] = "/static/8bitmoney.png"

        positions = stockstream.api.get_positions_by_player(scoped_username)
        player_profile = stockstream.positions.assemble_positions(positions)
        profile_stats = player_profile['profile_statistics']

        render._keywords['globals']['model'] = {
            'positions': positions,
            'player_profile': player_profile,
            'profile_stats': profile_stats,
            'twitch_user': channel
        }

        return render.pages.player()


class Portfolio:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    def GET(self, url):

        render._keywords['globals']['model'] = load_display_model()

        return render.pages.portfolio()


class Index:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    def GET(self, url):

        render._keywords['globals']['model'] = load_display_model()

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

debug = os.environ['DEBUG'] if 'DEBUG' in os.environ else None
if debug is not None:
    app.notfound = web.debugerror
else:
    app.notfound = render.pages.error

app.daemon = True

wsgi = app.wsgifunc()
wsgi = StaticMiddleware(wsgi)


if __name__ == '__main__':
    port = os.environ['PORT']

    options = {
        'bind': '%s:%s' % ('0.0.0.0', port),
        'workers': os.environ['WORKERS'],
    }
    StandaloneApplication(wsgi, options).run()
