from flask import Flask, render_template
from flask import url_for
from markupsafe import escape

app = Flask(__name__)

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

@app.route('/')
def home():
    return render_template('index.html', name=name, movies=movies)

@app.route('/home/<name>')
def hello(name:str):
    return f'<h1>Hello, {escape(name)}!</h1>'


@app.route('/test')
def url_test():
    print(url_for('home'))

    print(url_for('home', name='naive'))  

    print(url_for('url_test', age=2))
    
    return '<h1>Test page.</h1>'
