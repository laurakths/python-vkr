import os
import jwt
import hashlib
import time
import random
from flask import Blueprint, request, jsonify
from functools import wraps
from theory_data import THEORY, THEORY_RU, TOPICS_ORDER, TASKS_BANK

api_bp = Blueprint('api', __name__)

SECRET_KEY = os.environ.get('JWT_SECRET', 'python-compass-secret-key-2024')

# Временное хранилище пользователей
users_db = {}

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'No token'}), 401
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.current_user = payload
        except:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

# ============= АВТОРИЗАЦИЯ =============

@api_bp.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    
    if email in users_db:
        return jsonify({'success': False, 'error': 'Email уже зарегистрирован'})
    
    users_db[email] = {
        'name': data.get('name'),
        'surname': data.get('surname'),
        'class_name': data.get('class_name'),
        'password_hash': hashlib.sha256(data.get('password', '').encode()).hexdigest()
    }
    
    token = jwt.encode({'email': email, 'exp': time.time() + 86400}, SECRET_KEY, algorithm='HS256')
    return jsonify({'success': True, 'token': token})

@api_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password_hash = hashlib.sha256(data.get('password', '').encode()).hexdigest()
    
    user = users_db.get(email)
    if user and user['password_hash'] == password_hash:
        token = jwt.encode({'email': email, 'exp': time.time() + 86400}, SECRET_KEY, algorithm='HS256')
        return jsonify({'success': True, 'token': token, 'name': user['name']})
    
    return jsonify({'success': False, 'error': 'Неверный email или пароль'})

@api_bp.route('/api/user', methods=['GET'])
@login_required
def get_user():
    email = request.current_user['email']
    user = users_db.get(email, {})
    return jsonify({
        'name': user.get('name'),
        'surname': user.get('surname'),
        'class_name': user.get('class_name'),
        'email': email
    })

@api_bp.route('/api/update_profile', methods=['POST'])
@login_required
def update_profile():
    data = request.json
    email = request.current_user['email']
    if email in users_db:
        users_db[email]['name'] = data.get('name')
        users_db[email]['surname'] = data.get('surname')
        users_db[email]['class_name'] = data.get('class_name')
    return jsonify({'success': True})

# ============= ТЕОРИЯ =============

@api_bp.route('/api/theory')
@login_required
def get_theory():
    lang = request.args.get('lang', 'ru')
    theory = THEORY.get(lang, THEORY_RU)
    topics_list = []
    for topic in TOPICS_ORDER:
        if topic in theory:
            topics_list.append({
                "key": topic,
                "title": theory[topic]["title"],
                "content": theory[topic]["content"]
            })
    return jsonify(topics_list)

@api_bp.route('/api/topics')
@login_required
def get_topics():
    lang = request.args.get('lang', 'ru')
    theory = THEORY.get(lang, THEORY_RU)
    topics = []
    for topic in TOPICS_ORDER:
        if topic in theory:
            topics.append({"key": topic, "title": theory[topic]["title"]})
    return jsonify(topics)

# ============= ЗАДАНИЯ =============

@api_bp.route('/api/generate_task', methods=['POST'])
@login_required
def generate_task():
    data = request.json
    topic = data.get('topic', 'fun')
    lang = data.get('lang', 'ru')
    
    tasks = TASKS_BANK.get(topic, {}).get(lang, [])
    if tasks:
        task = random.choice(tasks)
    else:
        task = "Напишите программу, которая выводит 'Hello, World!'"
    
    return jsonify({"task": task})

@api_bp.route('/api/check_code', methods=['POST'])
@login_required
def check_code():
    data = request.json
    code = data.get('code', '')
    
    issues = []
    warnings = []
    
    # Проверка синтаксиса
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        issues.append(f"Синтаксическая ошибка: {e.msg}")
    
    # Проверка наличия print
    if 'print(' not in code:
        warnings.append("В коде нет print() - результат не будет выведен")
    
    # Проверка опасных модулей
    dangerous = ['import os', 'import subprocess', '__import__', 'eval(', 'exec(']
    for d in dangerous:
        if d in code:
            issues.append(f"Обнаружен небезопасный код: {d}")
    
    if issues:
        feedback = "❌ " + "\n❌ ".join(issues)
    elif warnings:
        feedback = "⚠️ " + "\n⚠️ ".join(warnings) + "\n\n✅ Код синтаксически верен"
    else:
        feedback = "✅ Код синтаксически верен!"
    
    return jsonify({"feedback": feedback})