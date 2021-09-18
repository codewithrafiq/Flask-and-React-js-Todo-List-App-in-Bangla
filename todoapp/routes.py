from todoapp import app
from todoapp.models import *



@app.route('/')
def home():
    return 'Hello, World!'