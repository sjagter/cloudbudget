import os
import json
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    if os.path.exists("tmp/cloudbudget-secrets.json"):
        with open("tmp/cloudbudget-secrets.json") as f:
            secrets = json.load(f)
            SECRET_KEY = secrets['cloudbudget-secret-key']
            SQLALCHEMY_DATABASE_URI = secrets['connection']
    else:
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'lame-secret-key'
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir,"app.db")}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

