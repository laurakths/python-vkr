from flask import Flask, send_from_directory
from flask_cors import CORS
from routes_api import api_bp
import os

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static',
            static_url_path='/static')
CORS(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'python-compass-secret-2024')

app.register_blueprint(api_bp)

# Главная страница
@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/login')
def login_page():
    return send_from_directory('templates', 'login.html')

@app.route('/profile')
def profile_page():
    return send_from_directory('templates', 'profile.html')

@app.route('/about')
def about_page():
    return send_from_directory('templates', 'about.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)