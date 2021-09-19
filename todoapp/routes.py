import re
from todoapp import app,db
from todoapp.models import Uses as User,Todo
from werkzeug.security import generate_password_hash, check_password_hash
from flask import json, request,jsonify
import uuid
import datetime
import jwt
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if "access-token" in request.headers:
            token = request.headers['access-token']
        if not token:
            return jsonify({"error":"Token is Required"})
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'],algorithms=["HS256"])
            login_user = User.query.filter_by(public_id=data['public_id']).first()
            if not login_user:
                return jsonify({"error":"No User Found"})
        except Exception as e:
            return jsonify({"error":str(e)})
        return f(login_user,*args, **kwargs)
    return decorator


@app.route('/')
@token_required
def home(login_user,*args, **kwargs):
    print("home login_user------------>",login_user)
    return jsonify({"message":"Hello World"})

@app.route("/api/register",methods=['POST'])
def register():
    data = request.get_json()
    print("data------->",data)
    try:
        hash_password = generate_password_hash(data['password'], method='sha256')
        user = User(email=data['email'], password=hash_password,public_id=str(uuid.uuid4()))
        db.session.add(user)
        db.session.commit()
        return jsonify({"message":"User was Created!"})
    except Exception as e:
        return jsonify({"error":str(e)})

@app.route("/api/login",methods=["POST"])
def login():
    data = request.get_json()
    print("login------->",data)
    if not data or not data["email"] or not data["password"]:
        return jsonify({"message":"Email and Password is Required."})
    user = User.query.filter_by(email=data["email"]).first()
    if not user:
        return jsonify({"message":"No user found."})
    if check_password_hash(user.password,data['password']):
        token = jwt.encode({"public_id":user.public_id,'exp':datetime.datetime.utcnow()+ datetime.timedelta(minutes=4500)},app.config['SECRET_KEY'],"HS256")
        return jsonify({"token":token})
    return jsonify({"message":"Somthing is Wrong.Try Again!"})