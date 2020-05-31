import os
basedir = os.path.abspath(os.path.dirname(__file__))



# import os
# from os.path import join, dirname
# from dotenv import load_dotenv
# from werkzeug.utils import secure_filename
#
# basedir = os.path.abspath(os.path.dirname(__file__))
#
# # Create .env file path.
# dotenv_path = join(dirname(__file__), '.env')
#
# load_dotenv(dotenv_path)
#
# # Accessing variables.
# url_trade = os.getenv('URL_TRADE')
# url_trade_id = os.getenv('URL_TRADE_ID')
# url_sign = os.getenv('URL_SIGN')
#
# login_trade = os.getenv('LOGIN_TRADE')
# password_trade = os.getenv('PASSWORD_TRADE')
#
# user = os.getenv('USER')
# password = os.getenv('PASSWORD')
#
# api_key = os.getenv('API_KEY')




class Configuration():
    DEBUG = True
    SECRET_KEY = 'you-will-never-guess'


    # Create in-memory database
    DATABASE_FILE = 'sample_db.sqlite'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, DATABASE_FILE)
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'JPG', 'docx', 'rar', 'zip']
    ALLOWED_EXTENSIONS_PHOTO = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.JPG', '.rar', '.zip']

