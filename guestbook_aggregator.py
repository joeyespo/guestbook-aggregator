"""
Guestbook Aggregator

Shows entries from all guestbooks using their APIs. Either set
the ENV variable GUESTBOOK_API_HOSTS or create a settings_local.py
to set the list of guestbooks.

API Endpoints this project accesses and expects:
- GET  /entries     -> {'entries': [<entry>]}
- POST /entries     -> {}
    - Payload
        - name : string
        - email : email
        - message : string
- GET  /entry/:id   -> <entry>

Objects
- <entry>
    - id : string
    - timestamp : datetime string
    - name : string
    - email : email
    - photo : url
    - message : string
"""


from __future__ import print_function

from urlparse import urljoin
from dateutil import parser
import requests
from flask import Flask, redirect, render_template, request, url_for


# Flask application
app = Flask(__name__)
app.config.from_pyfile('settings.py')
app.config.from_pyfile('settings_local.py', silent=True)
# Constants
API_SCHEME = app.config['GUESTBOOK_API_SCHEME']
API_HOSTS = app.config['GUESTBOOK_API_HOSTS'].split(';')


# Views
@app.route('/')
def index():
    try:
        entries = aggregate_entries()
        error = None
    except requests.exceptions.ConnectionError as ex:
        entries = []
        error = 'Error getting entries: ' + str(ex)
    return render_template('index.html', entries=entries, error=error)


@app.route('/<guestbook_host>/<entry_id>')
def view_entry(guestbook_host, entry_id):
    entry = load_entry(guestbook_host, entry_id)
    return render_template('entries/view.html', entry=entry)


@app.route('/new', methods=['GET', 'POST'])
def new_entry():
    if (request.method == 'GET'):
        return render_template('entries/new.html', hosts=API_HOSTS)

    url = urljoin(API_SCHEME + request.form['url'], '/entries')
    payload = {
        'name': request.form['name'],
        'email': request.form['email'],
        'message': request.form['message'],
    }
    r = requests.post(url, data=payload)
    if not r.ok:
        return r.text, r.status_code

    return redirect(url_for('index'))


# Helpers
def load_entry(guestbook_host, entry_id):
    url = urljoin(API_SCHEME + guestbook_host, '/entry/' + str(entry_id))

    # Get entry from guestbook
    try:
        r = requests.get(url)
        return r.json()
    except requests.exceptions.ConnectionError as ex:
        # Show an error as an entry
        return {
            'name': type(ex),
            'photo': url_for('static', filename='error.png'),
            'message': str(ex),
        }


def aggregate_entries():
    def add_host(entry, host):
        entry['host'] = host
        return entry

    # Get all entries from all guestbooks
    entries = []
    for host in API_HOSTS:
        try:
            # Request entries from the API
            url = urljoin(API_SCHEME + host, '/entries')
            r = requests.get(url)
            # Get entries
            data = r.json()
            guestbooke_entries = data['entries']
            # Add the source URL to the entry data
            guestbooke_entries = map(lambda e: add_host(e, host),
                guestbooke_entries)
            # Include the entries in the list
            entries += guestbooke_entries
        except requests.exceptions.ConnectionError as ex:
            # Show an error as an entry
            entries.append({
                'name': type(ex),
                'photo': url_for('static', filename='error.png'),
                'message': str(ex),
            })

    # Sort on the timestamp, if available
    entries.sort(key=lambda e: parser.parse(e['timestamp']) if e.get('timestamp') else None, reverse=True)

    return entries


# Run development server
if __name__ == '__main__':
    app.run(app.config['HOST'], app.config['PORT'], app.debug)
