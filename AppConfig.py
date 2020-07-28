import os

class AppConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret key'
