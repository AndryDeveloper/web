from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
#from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'
#migrate = Migrate(app, db)

from app import routes, models