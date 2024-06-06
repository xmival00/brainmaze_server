from flask import Blueprint, redirect, render_template, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from database.models import db, User

blueprint_auth = Blueprint('auth', __name__)

@blueprint_auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')


@blueprint_auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@blueprint_auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return 'Username already exists'
        new_user = User(username=username)
        new_user.set_password(password)
        if not new_user.role:  # Just in case, but not strictly necessary with the default set
            new_user.role = 'user'
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

