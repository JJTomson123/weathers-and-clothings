from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flaskblog import get3
from flaskblog import get7

get3.get3()
get7.get7()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ddff290515c29a5e706c9029f54a9c52'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flaskblog import routes