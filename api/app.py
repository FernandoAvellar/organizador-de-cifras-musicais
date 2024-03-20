from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
from psycopg2 import Error
from werkzeug.security import check_password_hash, generate_password_hash
from utilities import login_required, DatabaseUtility


# Configure lithurgical sessions in a catholic mass to sort sheet musics.
SESSOES_DA_MISSA = {
    1:  "Aclamação",
    2:  "Amém",
    3:  "Ato penitencial",
    4:  "Comunhão",
    5:  "Cordeiro",
    6:  "Consagração",
    7:  "Entrada",
    8:  "Geral",
    9:  "Glória",
    10: "Santo",
    11: "Saída",
    12: "Paz",
    13: "Ofertório"
}

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = DatabaseUtility()


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        if not (username and password):
            flash('Please, fill username and password', 'error')
            return redirect('/login')

        # Open connection, cursor and Query database for username
        # O banco postgress retorna uma tupla onde sua posição 0 é o id a 1 é o username e a 2 é o hash #
        db.connect()
        db.cursor.execute(
            "SELECT * FROM users WHERE username = %s", (username,))
        user_query = db.cursor.fetchall()

        if len(user_query) == 0:
            db.close()
            flash('Invalid user', 'error')
            return redirect("/login")
        elif not check_password_hash(user_query[0][2], password):
            db.close()
            flash('Invalid password.', 'error')
            return redirect("/login")
        else:
            # Remember which user has logged in
            session["user_id"] = user_query[0][0]
            session["username"] = user_query[0][1]
            flash('Logged in successfully.', 'info')
            db.close()
            return redirect("/")

    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not (username and password and confirm_password):
            flash('Please, fill all inputs!', 'error')
            return redirect('/register')

        if password != confirm_password:
            flash('Password does not match', 'error')
            return redirect('/register')

        # Insert new user into the database
        hash_password = generate_password_hash(password)
        db.connect()

        try:
            db.cursor.execute(
                "INSERT INTO users (username, hash) VALUES(%s, %s)", (username, hash_password))
            db.connection.commit()
            flash('User registered successfully.', 'info')
            db.close()
            return redirect("login")

        except (Exception, Error) as err:
            flash("Error in register new user", 'error')
            print("Error in register new user", err)
            db.close()
            return redirect("/register")

    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    # Forget any user_id, close database connections and redirect to login page
    session.clear()
    db.close()
    flash('Logged out successfully.', 'info')
    return redirect("/index")


@app.route("/list")
@login_required
def list():
    db.connect()
    db.cursor.execute("SELECT id, nome, sessao FROM cifras")
    sheets = db.cursor.fetchall()
    db.close()
    return render_template("list.html", sheets=sheets)


@app.route("/filter", methods=["GET", "POST"])
@login_required
def filter():
    selected_filters = []
    if request.method == "POST":
        # Get selected filters
        for section in SESSOES_DA_MISSA.values():
            if request.form.get(section):
                selected_filters.append(section)

        if selected_filters:
            # format list in Tuples to mount the correct query
            filter_string = ', '.join('%s' for _ in selected_filters)
            query = "SELECT id, nome, sessao FROM cifras WHERE sessao IN ({})".format(
                filter_string)

            # query database
            db.connect()
            db.cursor.execute(query, tuple(selected_filters))
            sheets = db.cursor.fetchall()
            db.close()

            return render_template("filter.html", sheets=sheets, sessions=SESSOES_DA_MISSA.values())

        else:
            db.connect()
            db.cursor.execute("SELECT id, nome, sessao FROM cifras")
            sheets = db.cursor.fetchall()
            db.close()

            return render_template("filter.html", sheets=sheets, sessions=SESSOES_DA_MISSA.values())

    else:
        db.connect()
        db.cursor.execute("SELECT id, nome, sessao FROM cifras")
        sheets = db.cursor.fetchall()
        db.close()
        return render_template("filter.html", sheets=sheets, sessions=SESSOES_DA_MISSA.values())


@app.route("/insert", methods=["GET", "POST"])
@login_required
def insert():
    if request.method == "POST":
        nome = request.form.get("name")
        sessao = request.form.get("session")
        cifra = request.form.get("music_sheet")

        if not (nome and sessao and cifra):
            flash('Please, fill all inputs!', 'error')
            return redirect('/insert')

        # insert new sheet music in database
        db.connect()

        try:
            db.cursor.execute(
                "INSERT INTO cifras (nome, sessao, cifra) VALUES(%s, %s, %s)", (nome, sessao, cifra))
            db.connection.commit()
            flash('New sheet music inserted successfully.', 'info')
            db.close()
            return redirect("/list")

        except (Exception, Error) as err:
            flash("Error in insert new sheet music", 'error')
            print("Error in insert new sheet music", err)
            db.close()
            return redirect("/list")

    else:
        # allow /insert route only accesible to admin user.
        if session["username"] != 'admin':
            return redirect('/')

        return render_template("insert.html", sessions=SESSOES_DA_MISSA.values())


@app.route("/generate", methods=["GET", "POST"])
@login_required
def generate():
    if request.method == "POST":
        input_list = request.form.get("list")
        selected_sheet_music_list = input_list.split(',')

        db.connect()
        try:
            with open("static/cifras_selecionadas.txt", "w") as file:
                for selected in selected_sheet_music_list:
                    selected = int(selected.strip())
                    db.cursor.execute(
                        "SELECT * FROM cifras WHERE id = %s", (selected,))
                    query = db.cursor.fetchone()
                    if query:
                        file.write(
                            f"{query[2]}\n\nMúsica: {query[1]}\n\n{query[3]}\n\n")

        except Exception as err:
            flash('Failed to generate repertoire', 'error')
            print('Failed to generate repertoire', err)

        finally:
            db.close()

        flash('Repertoire generated successfully.', 'info')

        return redirect('/generate')

    else:
        return render_template("generate.html")


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if session["username"] != 'admin':
        flash('User not authorized', 'error')
        return redirect('/index')

    db.connect()
    try:
        db.cursor.execute("DELETE FROM cifras WHERE id = %s", (id,))
        db.connection.commit()
        flash('Sheet music deleted successfully', 'info')
    except Exception as err:
        db.connection.rollback()
        flash('Failed to delete sheet music', 'error')
        print('Failed to delete sheet music', err)
    finally:
        db.close()

    return redirect("/list")


@app.route('/edit/<int:id>')
@login_required
def edit_cifra(id):
    if session["username"] != 'admin':
        flash('User not authorized', 'error')
        return redirect('/list')

    db.connect()
    try:
        db.cursor.execute("SELECT * FROM cifras WHERE id = %s", (id,))
        cifra_data = db.cursor.fetchone()
        sessions = SESSOES_DA_MISSA.values()
        return render_template('update.html', cifra_data=cifra_data, sessions=sessions)
    except Exception as err:
        flash('Failed to retrieve sheet music data', 'error')
        print('Failed to retrieve sheet music data', err)
        return redirect('/list')
    finally:
        db.close()


@app.route("/update/<int:id>", methods=["POST"])
@login_required
def update(id):
    nome = request.form.get("name")
    sessao = request.form.get("session")
    cifra = request.form.get("music_sheet")

    if not (nome and sessao and cifra):
        flash('Please, fill all inputs!', 'error')
        return redirect('/list')

    # allow /update route only accesible to admin user.
    if session["username"] != 'admin':
        flash('User not authorized', 'error')
        return redirect('/list')

    db.connect()
    try:
        db.cursor.execute(
            "UPDATE cifras SET nome = %s, sessao = %s, cifra = %s WHERE id = %s", (nome, sessao, cifra, id))
        db.connection.commit()
        flash('Sheet music updated successfully', 'info')
        return redirect('/list')
    except Exception as err:
        flash('Failed to update sheet music', 'error')
        print('Failed to update sheet music', err)
        return redirect('/list')
    finally:
        db.close()


@app.route('/cifra/<int:id>')
@login_required
def get_cifra(id):
    db.connect()
    try:
        db.cursor.execute("SELECT cifra FROM cifras WHERE id = %s", (id,))
        cifra_data = db.cursor.fetchone()
        if cifra_data:
            return cifra_data[0]
        else:
            flash('Sheet music not found', 'error')
            return redirect('/list')
    except Exception as err:
        flash('Failed to retrieve sheet music', 'error')
        print('Failed to retrieve sheet music', err)
        return redirect('/list')
    finally:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)
