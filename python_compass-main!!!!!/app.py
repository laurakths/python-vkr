from config import app, db
from models import User
from routes_auth import auth_bp
from routes_api import api_bp

app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
