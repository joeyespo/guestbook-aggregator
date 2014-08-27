"""
Default settings

Note: This file is under version control. Instead of changing settings
here, create a new settings_local.py file and add your variables there.
"""


import os


# Server settings
DEBUG = str(os.environ.get('DEBUG', False)) == 'True'
HOST = os.environ.get('HOST', 'localhost')
PORT = int(os.environ.get('PORT', 5000))
SECRET_KEY = os.environ.get('SECRET_KEY')


# 3rd-party settings
GUESTBOOK_API_SCHEME = os.environ.get('GUESTBOOK_API_SCHEME', 'http://')
GUESTBOOK_API_HOSTS = os.environ.get('GUESTBOOK_API_URLS', 'localhost:5000')
