from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///journal.db'
    app.config['SECRET_KEY'] = 'your-secret-key'

    # Initialize extensions
    db.init_app(app)

    # Import and register routes
    from app.routes.auth_routes import auth_bp
    from app.routes.journal_routes import journal_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(journal_bp)

    return app
