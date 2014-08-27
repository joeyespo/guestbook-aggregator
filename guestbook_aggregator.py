from __future__ import print_function

import urllib
import hashlib
from urlparse import urljoin
from dateutil import parser
import requests
from flask import Flask, render_template, request


# Flask application
app = Flask(__name__)
app.config.from_pyfile('settings.py')
app.config.from_pyfile('settings_local.py', silent=True)
# Constants
API_URLS = app.config['GUESTBOOK_API_URLS'].split(';')


# Views
@app.route('/')
def index():
    entries = aggregate_entries()
    return render_template('index.html', entries=entries)


# Helpers
def aggregate_entries():
    urls = map(lambda url: urljoin(url, '/entries'), API_URLS)
    entries = []
    for url in urls:
        r = requests.get(url)
        # TODO: handle errors
        data = r.json()
        entries += map(transform_entry, data['entries'])
    entries.sort(key=lambda x: x['timestamp'], reverse=True)
    return entries


def transform_entry(entry):
    return {
        'timestamp': parser.parse(entry['timestamp']),
        'author': entry['author'],
        'photo': gravatar(entry['author']),
        'message': entry['message'],
    }


def gravatar(email):
    email_hash = hashlib.md5(email.lower()).hexdigest()
    return 'http://www.gravatar.com/avatar/' + email_hash


# Run development server
if __name__ == '__main__':
    app.run(app.config['HOST'], app.config['PORT'], app.debug)
