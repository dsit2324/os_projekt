# Refactored Flask application with reorganized structure and different styling/structure

from flask import Flask, render_template_string, request, flash, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "tajnykey"),
    WTF_CSRF_ENABLED=False,
    SQLALCHEMY_DATABASE_URI="sqlite:///formdata.db",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SESSION_PERMANENT=False,
)

db = SQLAlchemy(app)

# --- Models ---
class FormData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    message = db.Column(db.Text, nullable=False)

# --- Forms ---
class MyForm(FlaskForm):
    name = StringField("Jméno", validators=[DataRequired("Povinné pole")])
    email = StringField("Email", validators=[DataRequired("Povinný email"), Email("Neplatný email")])
    gender = SelectField("Pohlaví", choices=[("muž", "Muž"), ("žena", "Žena")])
    message = TextAreaField("Zpráva", validators=[DataRequired("Povinné pole")])
    submit = SubmitField("Odeslat")

# --- Templates ---
MAIN_TEMPLATE = """
<!doctype html>
<html lang="cs">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Formulář</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background:#f4f6f9; }
        .card { border-radius:18px; box-shadow:0 10px 30px rgba(0,0,0,.08); }
        .brand { font-weight:700; }
    </style>
</head>
<body>
<nav class="navbar bg-white shadow-sm">
    <div class="container d-flex justify-content-between">
        <a href="{{ url_for('index') }}" class="navbar-brand brand">FORM APP</a>
        <div>
            {% if session.get('admin') %}
                <a href="{{ url_for('admin') }}" class="btn btn-outline-primary btn-sm">Admin</a>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-secondary btn-sm">Odhlásit</a>
            {% else %}
                <a href="{{ url_for('login') }}" class="btn btn-primary btn-sm">Přihlásit</a>
            {% endif %}
        </div>
    </div>
</nav>

<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-7 col-lg-5">
            <div class="card p-4">

                {% with msgs = get_flashed_messages() %}
                    {% if msgs %}
                        <div class="alert alert-success">{{ msgs[0] }}</div>
                    {% endif %}
                {% endwith %}

                <h3 class="text-center mb-4">Napište nám</h3>
                <form method="POST">
                    {{ form.hidden_tag() }}

                    <div class="mb-3">
                        {{ form.name.label(class="form-label") }}
                        {{ form.name(class="form-control", placeholder="Vaše jméno") }}
                    </div>

                    <div class="mb-3">
                        {{ form.email.label(class="form-label") }}
                        {{ form.email(class="form-control", placeholder="email@example.com") }}
                    </div>

                    <div class="mb-3">
                        {{ form.gender.label(class="form-label") }}
                        {{ form.gender(class="form-select") }}
                    </div>

                    <div class="mb-3">
                        {{ form.message.label(class="form-label") }}
                        {{ form.message(class="form-control", rows=4, placeholder="Vaše zpráva...") }}
                    </div>

                    <button class="btn btn-primary w-100" type="submit">Odeslat</button>
                </form>
            </div>
        </div>
    </div>
</div>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!doctype html>
<html lang="cs">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-4">
            <div class="card p-4 shadow-sm">
                <h4 class="text-center mb-3">Admin Login</h4>
                {% with msgs = get_flashed_messages() %}
                    {% if msgs %}
                        <div class="alert alert-danger">{{ msgs[0] }}</div>
                    {% endif %}
                {% endwith %}
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label">Uživatel</label>
                        <input type="text" name="username" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Heslo</label>
                        <input type="password" name="password" class="form-control" required>
                    </div>
                    <button class="btn btn-primary w-100">Přihlásit</button>
                </form>
            </div>
        </div>
    </div>
</div>
</body>
</html>
"""

ADMIN_TEMPLATE = """
<!doctype html>
<html lang="cs">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<nav class="navbar bg-white shadow-sm mb-4">
    <div class="container d-flex justify-content-between">
        <a href="{{ url_for('index') }}" class="navbar-brand">← Zpět</a>
        <a href="{{ url_for('logout') }}" class="btn btn-outline-secondary btn-sm">Odhlásit</a>
    </div>
</nav>

<div class="container">
    <h3 class="mb-3">Přijaté zprávy</h3>
    {% if items %}
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>#</th><th>Jméno</th><th>Email</th><th>Pohlaví</th><th>Zpráva</th><th></th>
                </tr>
            </thead>
            <tbody>
                {% for it in items %}
                <tr>
                    <td>{{ it.id }}</td>
                    <td>{{ it.name }}</td>
                    <td>{{ it.email }}</td>
                    <td>{{ it.gender }}</td>
                    <td>{{ it.message }}</td>
                    <td>
                        <form method="POST" action="{{ url_for('delete_entry', entry_id=it.id) }}" onsubmit="return confirm('Smazat?');">
                            <button class="btn btn-danger btn-sm">Smazat</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    {% else %}
        <div class="alert alert-info">Žádná data.</div>
    {% endif %}
</div>
</body>
</html>
"""

# --- Utility ---
def require_admin():
    return session.get("admin") is True

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    form = MyForm()
    if form.validate_on_submit():
        entry = FormData(
            name=form.name.data,
            email=form.email.data,
            gender=form.gender.data,
            message=form.message.data,
        )
        db.session.add(entry)
        db.session.commit()
        flash("Zpráva odeslána")
        return redirect(url_for('index'))
    return render_template_string(MAIN_TEMPLATE, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == 'admin':
            session['admin'] = True
            return redirect(url_for('admin'))
        flash("Neplatné údaje")
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if not require_admin():
        return redirect(url_for('login'))
    items = FormData.query.all()
    return render_template_string(ADMIN_TEMPLATE, items=items)

@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    if not require_admin():
        return redirect(url_for('login'))
    row = FormData.query.get_or_404(entry_id)
    db.session.delete(row)
    db.session.commit()
    return redirect(url_for('admin'))

# --- DB init ---
with app.app_context():
    db.create_all()
    try:
        info = db.session.execute(text("PRAGMA table_info(form_data)")).fetchall()
        cols = {c[1] for c in info}
        if 'gender' not in cols:
            db.session.execute(text("ALTER TABLE form_data ADD COLUMN gender VARCHAR(10) NOT NULL DEFAULT 'muž'"))
        if 'message' not in cols:
            db.session.execute(text("ALTER TABLE form_data ADD COLUMN message TEXT NOT NULL DEFAULT ''"))
        db.session.commit()
    except Exception:
        db.session.rollback()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
