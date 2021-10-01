from sqlalchemy.orm import session
from todoapp import app,db
from todoapp.models import Uses as User,Todo
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request,jsonify
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

@app.route("/api/add-get-todo",methods=["GET","POST"])
@token_required
def add_get_todo(login_user,*args, **kwargs):
    if request.method=="POST":
        try:
            title = request.get_json()["title"]
            new_todo = Todo(title=title,user_id=login_user.id)
            db.session.add(new_todo)
            db.session.commit()
            return jsonify({"message":"Todo Created !"})
        except Exception as e:
            return jsonify({"error":str(e)})
    user_todos = Todo.query.filter_by(user_id=login_user.id)
    all_todo=[]
    for todo in user_todos:
        single_todo = {}
        single_todo["id"] =todo.id
        single_todo["title"] =todo.title
        single_todo["data"] =todo.data
        all_todo.append(single_todo)
    return jsonify({"data":all_todo})

@app.route("/api/edit-delete-todo",methods=["DELETE","POST"])
@token_required
def edit_delete_todo(login_user,*args, **kwargs):
    if request.method == "POST":
        todoid = request.get_json()["todoid"]
        title = request.get_json()["title"]
        todo = Todo.query.filter_by(user_id=login_user.id,id=todoid).first()
        if not todo:
            return jsonify({"message":f"No Todo Found or This is not Your Todo !"})
        todo.title=title
        db.session.commit()
        return jsonify({"message":"Todo is Updated !"})
    if request.method == "DELETE":
        todoid = request.get_json()["todoid"]
        todo = Todo.query.filter_by(user_id=login_user.id,id=todoid).first()
        if not todo:
            return jsonify({"message":f"No Todo Found or This is not Your Todo !"})
        db.session.delete(todo)
        db.session.commit()
        return jsonify({"message":"Todo is Deleted Successfully!"})

@app.route("/api/get-todo/<todoid>")
@token_required
def getTodo(login_user,todoid,*args, **kwargs):
    todo = Todo.query.filter_by(user_id=login_user.id,id=todoid).first()
    single_todo = {}
    single_todo["id"] =todo.id
    single_todo["title"] =todo.title
    single_todo["data"] =todo.data
    return jsonify({"data":single_todo})

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
