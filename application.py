from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from ayuda import login_required
import os

app = Flask(__name__)

db = SQL("sqlite:///amiblog.db")

UPLOAD_FOLDER = './static/imgs/'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Session(app)

@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")
        lastname = request.form.get("lastname")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")


        user = db.execute("SELECT username FROM usuarios WHERE username = :username", username = username)
        if len(user) == 1:
            return render_template("register.html")

        if len(user) != 1 and password == confirm:
            a = db.execute("INSERT INTO usuarios (username, password, nombre, apellido) VALUES (:username,:password,:nombre, :apellido)", username = request.form.get("username"), password = generate_password_hash(password), nombre = name, apellido = lastname)
            print("a")
        session["user_id"] = a
        return redirect("/")
    else:
        return render_template("register.html")

@app.route('/')
@login_required
def inicio():
    username = db.execute("SELECT username FROM usuarios WHERE ID = :ID", ID = session["user_id"])
    return render_template("index.html", username = username[0]["username"])

@app.route('/login', methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        ingre = db.execute("SELECT * FROM usuarios WHERE username = :username",username=request.form.get("username"))

        if len(ingre) != 1:
            return render_template("login.html")

        contra = ingre[0]["password"]
        if not  check_password_hash(contra, password):
            print("socorro jesus")
            return render_template("login.html")
        else:
            print("Bendecido")
            session["user_id"] = ingre[0]["ID"]
            return redirect("/")
    else:
        return render_template("login.html")


@app.route('/config', methods=["GET", "POST"])
@login_required
def config():
    if request.method == "POST":
        nombre = request.form.get("name")
        apellido = request.form.get("lastname")
        description = request.form.get("acercade")

        descripcion = db.execute("UPDATE usuarios SET descripcion = :descripcion WHERE ID = :ID", descripcion = description, ID = session["user_id"])
        nombre = db.execute("UPDATE usuarios SET nombre = :nombre WHERE ID = :ID", nombre = nombre, ID = session["user_id"])
        apellido = db.execute("UPDATE usuarios SET apellido = :apellido WHERE ID = :ID", apellido= apellido, ID = session["user_id"])

        return redirect("/perfil")
    else:
        nombre = db.execute("SELECT nombre FROM usuarios WHERE ID = :ID", ID = session["user_id"])
        apellido = db.execute("SELECT apellido FROM usuarios WHERE ID = :ID", ID = session["user_id"])
        descripcion1 = db.execute("SELECT descripcion FROM usuarios WHERE ID = :ID", ID = session["user_id"])
        username = db.execute("SELECT username FROM usuarios WHERE ID = :ID", ID = session["user_id"])
        return render_template("config.html", descripcion = descripcion1[0]["descripcion"], nombre = nombre[0]["nombre"], apellido = apellido[0]["apellido"], username = username[0]["username"])


@app.route('/nuevopost', methods=["GET", "POST"])
@login_required
def nuevopost():
    if request.method == "POST":
        descripcion = request.form.get("description")
        #db.execute("INSERT INTO post (autor, description, img, hora) VALUES (:autor, :description, :img, :hora)", autor = session["user_id"], description = description, )

        if "imagen" not in request.files:
            print("socorro")
            return render_template("subir.html")
        file = request.files['imagen']

        if file:
            print("xd")
            nombre = file.filename
            a = file.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre))
            descrip = db.execute("INSERT INTO post (autor, description, hora) VALUES(:autor, :description, datetime('now'))",autor = session["user_id"], description = descripcion, )
            return redirect("/")
        else:
            return render_template("subir.html")
    else:
        username = db.execute("SELECT username FROM usuarios WHERE ID = :ID", ID = session["user_id"])
        return render_template("subir.html", username = username[0]["username"])


@app.route('/perfil', methods=["GET", "POST"])
@login_required
def perfil():
    if request.method == "POST":
        descripcion = db.execute("SELECT descripcion FROM usuarios WHERE ID = :ID", ID = session["user_id"])
        return render_template("perfil.html", descripcion)
    else:
        nombre = db.execute("SELECT nombre FROM usuarios WHERE ID = :ID", ID = session["user_id"])
        apellido = db.execute("SELECT apellido FROM usuarios WHERE ID = :ID", ID = session["user_id"])
        username = db.execute("SELECT username FROM usuarios WHERE ID = :ID", ID = session["user_id"])
        descripcion = db.execute("SELECT descripcion FROM usuarios WHERE ID = :ID", ID = session["user_id"])
        print("a")
        return render_template("perfil.html", username = username[0]["username"], nombre = nombre[0]["nombre"], apellido = apellido[0]["apellido"], descripcion = descripcion[0]["descripcion"])


@app.route("/salir")
def salir():

    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)