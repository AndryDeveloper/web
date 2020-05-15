import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Configuration():
    DEBUG = True
    SECRET_KEY = 'you-will-never-guess'


    # Create in-memory database
    DATABASE_FILE = 'sample_db.sqlite'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, DATABASE_FILE)
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
