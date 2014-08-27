import os


# Server settings
DEBUG = str(os.environ.get('DEBUG', False)) == 'True'
HOST = os.environ.get('HOST', 'localhost')
PORT = int(os.environ.get('PORT', 5000))
SECRET_KEY = os.environ.get('SECRET_KEY')


# 3rd-party settings
GUESTBOOK_API_URLS = os.environ.get('GUESTBOOK_API_URLS', '')
