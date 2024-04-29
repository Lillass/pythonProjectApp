from flask import Flask
from routes.routes import app_route
from flask_sqlalchemy import SQLAlchemy
from engine.db import db
from engine.login import login_manager
from models.models import User

app = Flask(__name__)
app.register_blueprint(app_route)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moex.db'
app.config['SECRET_KEY'] = 'very secret key'
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

def create_app():
    app = Flask(__name__)
    app.register_blueprint(app_route)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moex.db'

    db = SQLAlchemy(app)
    # db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)