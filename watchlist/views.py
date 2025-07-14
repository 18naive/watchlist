from flask import request, redirect, url_for, flash, render_template
from flask_login import current_user, login_user, logout_user, login_required
from watchlist import app, db
from watchlist.models import User, Movie

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
        
        user = db.session.scalar(db.select(User).limit(1))
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))
        flash('Invalid username or password.')
        return redirect(url_for('login'))
    
    return render_template('login.html')


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))
        current_user.name = name
        db.session.commit()
        flash('Settings updated successfully.')
        return redirect(url_for('index'))

    return render_template('settings.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))



@app.route('/', methods=['GET', 'POST'])
def index():
    """Display & create data."""
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(title) > 60 or len(year) != 4:
            flash('Invalid input.')
            return redirect(url_for('index'))
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created successfully.')
        return redirect(url_for('index'))
    # GET
    movies = db.session.scalars(db.select(Movie)).all()
    return render_template('index.html', movies=movies)


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = db.session.scalar(db.select(Movie).where(Movie.id == movie_id))
    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(title) > 60 or len(year) != 4:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated successfully.')
        return redirect(url_for('index'))
    # GET
    return render_template('edit.html', movie=movie)


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    movie = db.session.scalar(db.select(Movie).where(Movie.id == movie_id))
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted successfully.')
    return redirect(url_for('index'))