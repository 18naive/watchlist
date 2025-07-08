from flask import Flask
from flask import url_for
from markupsafe import escape

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Welcome to my Watchlist. <br /><img src="http://helloflask.com/totoro.gif" /></h1>'

@app.route('/home/<name>')
def hello(name:str):
    return f'<h1>Hello, {escape(name)}!</h1>'


@app.route('/test')
def url_test():
    print(url_for('home'))

    print(url_for('home', name='naive'))  

    print(url_for('url_test', age=2))
    
    return '<h1>Test page.</h1>'
