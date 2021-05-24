from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

db = SQL("sqlite:///amiblog.db")

@app.route('/')
def inicio():
    return render_template("index.html")

@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")
        lastname = request.form.get("lastname")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        if not username or not password or not confirm:
            return render_template("register.html")

        user = db.execute("SELECT username FROM usuarios WHERE username = :username", username = username)
        if len(user) == 1:
            return render_template("register.html")

        if len(user) != 1 and password == confirm:
            db.execute("INSERT INTO usuarios (username, password, nombre, apellido) VALUES (:username,:password,:nombre, :apellido)", username = request.form.get("username"), password = generate_password_hash(password), nombre = name, apellido = lastname)
            print("a")
        return redirect("/")
    else:
        return render_template("register.html")


