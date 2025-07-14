import os, sys
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


# win or posix.
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), os.getenv('DATABASE_FILE', 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


login_manager = LoginManager(app)
login_manager.login_view = 'login'


# load user
@login_manager.user_loader
def load_user(user_id):
    from watchlist.models import User
    return db.session.get(User, int(user_id))


# inject variable
@app.context_processor
def inject_user():
    from watchlist.models import User
    user = db.session.scalar(db.select(User).limit(1))
    return dict(user=user)


from watchlist import views, commands, errors