from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate



app = Flask(__name__)
app.config['SECRET_KEY'] = 'fcb0e5de6f974c559d193710228cfcf2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todoapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)



from todoapp import routes