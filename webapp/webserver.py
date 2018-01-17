import json
import locale
import os
from datetime import datetime, timedelta
import bleach
import web
import markdown
from cached import cached

from urllib import unquote
import posixpath
import stockstream
import tradingview_api
import robinhood
import scrub
from gunicorn.app.base import BaseApplication
import twitch_api
import config

import gunicorn.app.base

from gunicorn.six import iteritems

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

t_globals = dict(datestr=web.datestr,
                 round=round,
                 stockstream=stockstream,
                 robinhood=robinhood,
                 tradingview_api=tradingview_api,
                 datetime=datetime,
                 api_endpoint=config.SS_API_ENDPOINT,
                 scrub=scrub,
                 locale=locale,
                 json=json,
                 str=str,
                 bleach=bleach)

urls = (
    '/referral', 'Referral',
    '/robots.txt', 'Robots',
    '/info/*(.+)', 'Info',
    '/scores*(.+)', 'Scores',
    '/register*(.+)', 'Register',
    '/contest*(.+)', 'Contest',
    '/symbol/*(.+)', 'Symbol',
    '/portfolio*(.+)', 'Portfolio',
    '/player/*(.+)', 'Player',
    '/dashboard*(.+)', 'Dashboard',
    '/charts*(.+)', 'Charts',
    '/*(.+)', 'Index',
)


class StockStreamWebApp(web.application):
    def run(self, *middleware):
        port = 8080
        if 'PORT' in os.environ:
            port = os.environ['PORT']
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

render = web.template.render('templates/', globals=t_globals, cache=False)
render._keywords['globals']['render'] = render


class Robots:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    def GET(self):
        return "User-agent: *\nAllow: /"


class Referral:
    def __init__(self):
        pass

    def POST(self, url):
        referral_code = stockstream.api.get_referral_code()
        raise web.seeother(referral_code)

    def GET(self):
        referral_code = stockstream.api.get_referral_code()
        raise web.seeother(referral_code)


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

    @cached()
    def GET(self, url):
        page_model = {
                'portfolio_values': stockstream.api.get_portfolio_values(),
                'portfolio_stats': stockstream.portfolio.compute_portfolio_statistics(),
                'orders': stockstream.api.get_orders_today(),
            }

        return render.pages.charts(page_model)


class Scores:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    def GET(self, url):

        ranked_scores = stockstream.scores.get_ranked_scores()

        page_model = {
            'ranked_scores': ranked_scores
        }

        return render.pages.scores(page_model)


class Contest:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    def GET(self, url):

        page_model = {

        }

        return render.pages.contest(page_model)


class Register:
    def __init__(self):
        pass

    def POST(self, url):
        post_data = web.input(twitch_username="", email="", zip_code="", captcha="")

        registration_object = {
            "platform": "twitch",
            "email_address": post_data.email,
            "username": post_data.twitch_username,
            "zip_code": post_data.zip_code,
            "g_recaptcha_response": post_data['g-recaptcha-response']
        }

        response = stockstream.api.register_contest_player(registration_object)

        page_model = {
            "register_response": response
        }

        return render.pages.register_response(page_model)

    def GET(self, url):

        page_model = {
        }

        return render.pages.register(page_model)


class Symbol:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    @cached()
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

        page_model = {
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

        return render.pages.symbol(symbol, page_model)


class Player:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    @cached()
    def GET(self, scoped_username):
        scoped_username = scoped_username.lower()
        name = scoped_username.split(":")[1]
        channel = twitch_api.get_channel_for_user(name)

        positions = stockstream.api.get_positions_by_player(scoped_username)
        player_profile = stockstream.positions.assemble_positions(positions)
        profile_stats = player_profile['profile_statistics']
        wallet = stockstream.api.get_wallet_for_user(scoped_username)
        registration_status = stockstream.api.get_registration_status(scoped_username)

        page_model = {
            'positions': positions,
            'player_profile': player_profile,
            'profile_stats': profile_stats,
            'twitch_user': channel,
            'wallet': wallet,
            'registration_status': registration_status
        }

        return render.pages.player(page_model)


class Portfolio:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    @cached()
    def GET(self, url):

        portfolio = stockstream.api.get_current_portfolio()
        portfolio_stats = stockstream.portfolio.compute_portfolio_statistics()

        if url == ".csv":
            rows = []
            for symbol in portfolio_stats['asset_stats']:
                stats = portfolio_stats['asset_stats'][symbol]
                if len(rows) == 0:
                    rows.append(",".join(stats.keys()))
                rows.append(",".join(str(value) for value in stats.values()))

            return "\n".join(rows)
        elif url == ".json":
            return json.dumps(portfolio_stats['asset_stats'])

        page_model = {
                'portfolio_values': stockstream.api.get_portfolio_values(),
                'portfolio_stats': portfolio_stats,
                'portfolio': portfolio,
                'order_stats': stockstream.api.get_order_stats(),
                'orders': stockstream.api.get_orders_today(),
            }

        page = render.pages.portfolio(page_model)

        return page


class Dashboard:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    @cached()
    def GET(self, url):

        date_str = robinhood.api.find_last_market_open_date()

        positions = stockstream.api.get_positions_by_date(date_str)
        date_profile = stockstream.positions.assemble_positions(positions)
        portfolio_values = stockstream.api.get_portfolio_values_by_date(date_str)
        if portfolio_values is None:
            portfolio_values = []

        page_model = {
                'date_profile': date_profile,
                'portfolio_values': portfolio_values,
                'positions': positions,
                'date_str': date_str
            }

        page = render.pages.dashboard(page_model)

        return page


class Index:
    def __init__(self):
        pass

    def POST(self, url):
        raise web.seeother('/')

    @cached()
    def GET(self, url):

        page_model = {
                'portfolio_values': stockstream.api.get_portfolio_values(),
                'portfolio_stats': stockstream.portfolio.compute_portfolio_statistics(),
                'order_stats': stockstream.api.get_order_stats(),
                'orders': stockstream.api.get_orders_today(),
                'portfolio': stockstream.api.get_current_portfolio(),
                'ranked_scores': stockstream.scores.get_ranked_scores()
            }

        page = render.pages.index(page_model)

        return page


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
