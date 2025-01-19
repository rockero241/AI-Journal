from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    return "Login Page"

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return "Register Page"
