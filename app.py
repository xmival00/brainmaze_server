# Imports
import os

# Flask imports
from flask import Flask, redirect, url_for, request, render_template
from flask_login import LoginManager, current_user

# Local imports
from database.models import db, User, Subject
from blueprints.user.views import blueprint_auth
from blueprints.subjects.views import blueprint_subjects
from blueprints.eeg.views import blueprint_eeg

def create_app():
    app = Flask(__name__)
    
    # Authentication
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Create tables if not exist
    db.app = app
    db.init_app(app)
    with app.app_context():
        if not os.path.exists('users.db'):
            db.create_all()

    # Register blueprints
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            subjects = Subject.query.all()  # Fetch all subjects from the database
            return render_template('index.html', subjects=subjects)
        else:
            return redirect(url_for('auth.login'))
    app.register_blueprint(blueprint_auth)
    app.register_blueprint(blueprint_subjects)
    app.register_blueprint(blueprint_eeg)
    
    return app

if __name__ == "__main__":

    app = create_app()
    app.run(ssl_context='adhoc', debug=True)
