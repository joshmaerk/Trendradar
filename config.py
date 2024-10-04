import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Ihr_sicherer_Schlüssel'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,'instance', 'trends.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False