#!/usr/bin/env python

import web

urls = ('/(.*)', 'Index')

application = web.application(urls, globals())
web.config.debug = True

class Index:

    def GET(self, name=''):
        return 'Hello World'

    def POST(self, name=''):
        return 'Hello World'

if __name__ == '__main__':application.run()