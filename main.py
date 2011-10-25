#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import urllib2

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

from spellingtable import spellingtable, dialects

class MainHandler(webapp.RequestHandler):

    template = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')

    def get(self):
        template_values = {'dialects': dialects}
        self.response.out.write(template.render(self.template, template_values))


def getspelling(q, dialect=5):
    dialecttable = spellingtable[int(dialect)]
    return [dialecttable.get(char.upper(), '') for char in q if char.strip()]

class SpellHandler(webapp.RequestHandler):

    template = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')

    def post(self):
        q = self.request.get('q', '')
        dialect = self.request.get('dialect', 5)
        lang = self.request.get('lang', 'de')

        spelling_list = getspelling(q, dialect)

        words = '+'.join(spelling_list)
        audio_url = '/play?lang=%s&q=%s&dialect=%s' % (lang, words, dialect)
        template_values = {'dialects': dialects,
                           'spelling_list': spelling_list,
                           'active_dialect': dialect,
                           'audio_url': audio_url}
        self.response.out.write(template.render(self.template, template_values))

    get = post

class AudioHandler(webapp.RequestHandler):

    def get(self):
        q = self.request.get('q', 'awesome')
        dialect = self.request.get('dialect', 5)
        lang = self.request.get('lang', 'de')

        words = '+'.join(getspelling(q, dialect))
        ua = self.request.headers.get('User-Agent'
            "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11")

        url = 'http://translate.google.com/translate_tts?tl=%s&q=%s' % (lang, words)
        headers = {'User-Agent': ua}
        req = urllib2.Request(url, headers=headers)

        r = urllib2.urlopen(req)
        c = r.read()
        r.close()
        self.response.headers.add_header("Content-Type", "audio/mpeg3")
        self.response.out.write(c)


def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/spell', SpellHandler),
                                          ('/play', AudioHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
