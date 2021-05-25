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

        if not username or not password or not confirm or not name or not lastname:
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

@app.route('/login', methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("login.html")

        ingre = db.execute("SELECT * FROM usuarios WHERE username = :username",username=request.form.get("username"))

        if len(ingre) != 1:
            return render_template("login.html")

        contra = ingre[0]["password"]
        if not  check_password_hash(contra, password):
            return render_template("login.html")
        else:
            return redirect("/")
            session["ID"] = ingre[0]["ID"]
    else:
        return render_template("login.html")
        
if __name__ == "__main__":
    app.run(debug=True)