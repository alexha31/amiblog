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
            flash('El nombre de usuario ya está en uso', 'error')
            return render_template("register.html")

        if password != confirm:
            flash('Las contraseñas no coinciden', 'error')
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
    flash('Bienvenido', 'success')
    username = db.execute("SELECT username FROM usuarios WHERE ID = :ID", ID = session["user_id"])
    posts = db.execute("SELECT p.*, u.username FROM post p INNER JOIN usuario u on u.id_user = p.autor ORDER BY p.id_post DESC")
    #comentarios =db.execute("SELECT c.*, u.username FROM comentarios c INNER JOIN usuarios u on u.ID = c.id_user")

    print(username)
    return render_template("index.html", username = username[0]["username"], posts = posts)

@app.route('/login', methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        rows = db.execute("select * from usuario where username = :username", username = username)
        if len(rows) == 0:
            return render_template("login.html", error="Usuario no existe")
        password_db = rows[0]["password"]
        if not check_password_hash(password_db, password):
            return render_template("login.html", error="contraseña incorrecta")
        else:
            session["id_user"] = rows[0]["id_user"]
            return redirect("/")
    else:
        return render_template("login.html")

        #Error = None
        '''ingre = db.execute("SELECT * FROM usuarios WHERE username = :username",username=request.form.get("username"))

        if len(ingre) != 1:
            flash('Su nombre de usuario es incorrecto', 'error')
            return render_template("login.html")

        contra = ingre[0]["password"]
        if not  check_password_hash(contra, password):
            print("socorro jesus")
            Error = 'Invalid credentials'
            flash('Su contraseña es incorrecta')
            return render_template("login.html")
        else:
            print("Bendecido")
            session["user_id"] = ingre[0]["ID"]
            return redirect("/")
    else:
        return render_template("login.html")'''


@app.route('/editarperfil', methods=["GET", "POST"])
@login_required
def editarperfil():
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


@app.route('/config', methods=["GET", "POST"])
@login_required
def cancelar():
    return redirect("/perfil")

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
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre))
            img = os.path.join(app.config["UPLOAD_FOLDER"], nombre)
            a = db.execute("INSERT INTO post (autor, description, img) VALUES(:autor, :description, :img)",autor = session["user_id"], description = descripcion, img = img)
            return redirect("/")
        else:
            return render_template("subir.html")
    else:
        username = db.execute("SELECT username FROM usuarios WHERE ID = :ID", ID = session["user_id"])
        return render_template("subir.html", username = username[0]["username"])

@app.route('/', methods=["GET", "POST"])
@login_required
def postcomment():
    if request.method == "POST":
        comentario = request.form.get("comentario")
        #db.execute("INSERT INTO comentarios (id_post, id_user, descripcion) VALUES (:id_post, :id_user, :descripcion)", id_post = . id_user = session["user_id"], descripcion = descripcion)
        return render_template("index.html")

@app.route('/<username>')
@login_required
def perfiles(username):

    x = db.execute("SELECT username FROM usuarios WHERE ID = :ID", ID = session["user_id"])
    if username == x[0]["username"]:
        return redirect("/perfil")

    lista = db.execute("SELECT * FROM usuarios WHERE username = :username", username = username)
    nombre = lista[0]["nombre"]
    apellido = lista[0]["apellido"]
    username1 = username
    descripcion = lista[0]["descripcion"]
    username = db.execute("SELECT username FROM usuarios WHERE ID = :ID", ID = session["user_id"])


    if descripcion == None:
            descripcion = ""
    #db.execute("SELECT nombre FROM usuarios WHERE ID = :ID", ID = session["user_id"])

    return render_template("perfiles.html", nombre = nombre, apellido = apellido, username1 = username1, descripcion = descripcion, username = username[0]["username"])

"""@app.route('/comentarios', methods=["GET", "POST"])
@login_required
def comments():"""

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
        if descripcion == None:
            descripcion = ""
        print("a")
        return render_template("perfil.html", username = username[0]["username"], nombre = nombre[0]["nombre"], apellido = apellido[0]["apellido"], descripcion = descripcion[0]["descripcion"])

@app.route("/eliminarpost", methods=["POST"])
def eliminar():
    id_post = request.form.get("id_post")
    db.execute(f"DELETE FROM post WHERE postid={id_post}")
    return redirect("/")

@app.route("/salir")
def salir():

    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=7000)