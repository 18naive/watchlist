import os, sys, click
from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy 
from markupsafe import escape

app = Flask(__name__)

# win or posix.
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# register command tha initial database.
@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def init_db(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')

# manage tables by class.
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20))

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(20))
    year = db.Column(db.String(4))

# register command tha generate fake data.
@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    name = 'Naive'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Done.')

# inject avariable
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def index():
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)

@app.route('/home/<name>')
def hello(name:str):
    return f'<h1>Hello, {escape(name)}!</h1>'


@app.route('/test')
def url_test():
    print(url_for('home'))

    print(url_for('home', name='naive'))  

    print(url_for('url_test', age=2))
    
    return '<h1>Test page.</h1>'
