from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import db
from models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
@login_required
def index():
    return render_template('index.html')


@auth_bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    return render_template('login.html')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    surname = data.get('surname')
    class_name = data.get('class_name')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'Email уже зарегистрирован'})

    password_hash = generate_password_hash(password)
    user = User(name=name, surname=surname, class_name=class_name, email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return jsonify({'success': True})


@auth_bp.route('/login_post', methods=['POST'])
def login_post():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Неверный email или пароль'})


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@auth_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    data = request.json
    current_user.name = data.get('name')
    current_user.surname = data.get('surname')
    current_user.class_name = data.get('class_name')
    db.session.commit()
    return jsonify({'success': True})


@auth_bp.route('/api/is_authenticated')
def is_authenticated():
    return jsonify({
        'authenticated': current_user.is_authenticated,
        'name': current_user.name if current_user.is_authenticated else None
    })


@auth_bp.route('/about')
def about():
    return render_template('about.html')
