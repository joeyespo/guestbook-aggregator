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
API_URLS = app.config['GUESTBOOK_API_URLS'].split(';')


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


@app.route('/<entry>')
def view_entry(id):
    entry = load_entry(id)
    return render_template('entries/view.html', entry=entry)


@app.route('/new', methods=['GET', 'POST'])
def new_entry():
    if (request.method == 'GET'):
        return render_template('entries/new.html', urls=API_URLS)

    url = urljoin(request.form['url'], '/entries')
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
def load_entry(guestbook_url, id):
    url = urljoin(guestbook_url, '/entry/' + str(id))

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
    urls = map(lambda url: urljoin(url, '/entries'), API_URLS)

    # Get all entries from all guestbooks
    entries = []
    for url in urls:
        try:
            r = requests.get(url)
            data = r.json()
            entries += data['entries']
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
