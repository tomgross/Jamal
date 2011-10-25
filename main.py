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
from operator import itemgetter

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

from spellingtable import spellingtable, dialects


def getspelling(q, dialect=5):
    dialecttable = spellingtable[int(dialect)]
    return [dialecttable.get(char.upper(), '') for char in q if char.strip()]

supported_langs = {'en': 'English',
                   'de': 'German',
                   'fr': 'French',
                   'ru': 'Russian',
                   'es': 'Spanish',
                   'it': 'Italian'}

class SpellHandler(webapp.RequestHandler):

    template = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')

    def get(self):
        q = self.request.get('q', '')
        dialect = self.request.get('dialect', 0)
        lang = self.request.get('lang', 'de')

        spelling_list = getspelling(q, dialect)

        words = ' '.join(spelling_list)
        host = 'http://localhost:8080'

        # XXX for some unknown reason WP-player only supports one query string
        # parameter. let's concat our values
        qs = urllib2.quote('%s*%s*%s' % (q, lang, dialect))
        langs = supported_langs.items()
        langs.sort(key=itemgetter(0))

        audio_url = '%s/play?qs=%s' % (host, qs)
        template_values = {'dialects': dialects,
                           'spelling_list': spelling_list,
                           'active_dialect': int(dialect),
                           'supported_langs': langs,
                           'active_lang': lang,
                           'audio_url': audio_url}
        self.response.out.write(template.render(self.template, template_values))

    post = get

class AudioHandler(webapp.RequestHandler):

    def get(self):
        qs = self.request.get('qs')
        q, lang, dialect = urllib2.unquote(qs).split('*')

        words = '+'.join(getspelling(q, dialect))
        ua = self.request.headers.get('User-Agent',
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
    application = webapp.WSGIApplication([('/', SpellHandler),
                                          ('/spell', SpellHandler),
                                          ('/play', AudioHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
