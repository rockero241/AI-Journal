import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///journal.db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
