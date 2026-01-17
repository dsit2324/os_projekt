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

# ---------- MODELS ----------
class FormData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    message = db.Column(db.Text, nullable=False)

# ---------- FORMS ----------
class MyForm(FlaskForm):
    name = StringField("Jméno", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    gender = SelectField("Kategorie", choices=[
        ("technický", "Technický problém"),
        ("ucet", "Problém s účtem"),
        ("dotaz", "Obecný dotaz"),
    ])
    message = TextAreaField("Popis problému", validators=[DataRequired()])
    submit = SubmitField("Odeslat požadavek")

# ---------- TEMPLATES ----------
MAIN_TEMPLATE = """
<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Support Desk</title>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">

<style>
body {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #eef2f7, #f8fafc);
}

.navbar-brand {
    font-weight: 700;
    color: #2563eb;
}

.card {
    border-radius: 18px;
    border: none;
    box-shadow: 0 20px 50px rgba(0,0,0,.08);
}

.badge-support {
    background: #e0f2fe;
    color: #0369a1;
}

.btn-primary {
    background: linear-gradient(90deg, #2563eb, #0ea5e9);
    border: none;
}

.btn-primary:hover {
    opacity: .9;
}

.form-control:focus, .form-select:focus {
    box-shadow: 0 0 0 3px rgba(37,99,235,.2);
    border-color: #2563eb;
}
</style>
</head>

<body>

<nav class="navbar bg-white shadow-sm">
    <div class="container d-flex justify-content-between">
        <span class="navbar-brand">🛟 Support Desk</span>
        <div>
            {% if session.get('admin') %}
                <a href="{{ url_for('admin') }}" class="btn btn-outline-primary btn-sm">Přehled</a>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-secondary btn-sm">Odhlásit</a>
            {% else %}
                <a href="{{ url_for('login') }}" class="btn btn-primary btn-sm">Admin</a>
            {% endif %}
        </div>
    </div>
</nav>

<div class="container py-5">
<div class="row justify-content-center">
<div class="col-lg-6">

<div class="card p-5">

{% with msgs = get_flashed_messages() %}
{% if msgs %}
<div class="alert alert-success text-center">
✅ Požadavek byl úspěšně odeslán. Ozveme se co nejdříve.
</div>
{% endif %}
{% endwith %}

<div class="text-center mb-4">
    <span class="badge badge-support mb-2">Zákaznická podpora</span>
    <h3 class="fw-bold mt-2">Nahlásit problém</h3>
    <p class="text-muted">Popište svůj problém – náš tým vám pomůže.</p>
</div>

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

<div class="mb-4">
    {{ form.message.label(class="form-label") }}
    {{ form.message(class="form-control", rows=5, placeholder="Popište problém co nejpodrobněji…") }}
</div>

<button class="btn btn-primary w-100 py-2">
📨 Odeslat požadavek
</button>
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
<title>Admin Login</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>

<body class="bg-light">
<div class="container py-5">
<div class="row justify-content-center">
<div class="col-md-4">

<div class="card p-4 shadow-sm">
<h4 class="text-center fw-bold mb-3">Admin – Support Desk</h4>

{% with msgs = get_flashed_messages() %}
{% if msgs %}
<div class="alert alert-danger">{{ msgs[0] }}</div>
{% endif %}
{% endwith %}

<form method="POST">
<input class="form-control mb-3" name="username" placeholder="Uživatel" required>
<input type="password" class="form-control mb-3" name="password" placeholder="Heslo" required>
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
<title>Support – Přehled</title>
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
<h3 class="fw-bold mb-3">📋 Přijaté požadavky</h3>

{% if items %}
<table class="table table-hover align-middle">
<thead class="table-light">
<tr>
<th>ID</th><th>Jméno</th><th>Email</th><th>Kategorie</th><th>Popis</th><th></th>
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
<form method="POST" action="{{ url_for('delete_entry', entry_id=it.id) }}">
<button class="btn btn-sm btn-danger">Vyřešeno</button>
</form>
</td>
</tr>
{% endfor %}
</tbody>
</table>
{% else %}
<div class="alert alert-info">Žádné otevřené požadavky.</div>
{% endif %}
</div>
</body>
</html>
"""

# ---------- UTILS ----------
def require_admin():
    return session.get("admin") is True

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def index():
    form = MyForm()
    if form.validate_on_submit():
        db.session.add(FormData(
            name=form.name.data,
            email=form.email.data,
            gender=form.gender.data,
            message=form.message.data
        ))
        db.session.commit()
        flash("ok")
        return redirect(url_for("index"))
    return render_template_string(MAIN_TEMPLATE, form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin":
            session["admin"] = True
            return redirect(url_for("admin"))
        flash("Neplatné údaje")
    return render_template_string(LOGIN_TEMPLATE)

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("index"))

@app.route("/admin")
def admin():
    if not require_admin():
        return redirect(url_for("login"))
    return render_template_string(ADMIN_TEMPLATE, items=FormData.query.all())

@app.route("/delete/<int:entry_id>", methods=["POST"])
def delete_entry(entry_id):
    if not require_admin():
        return redirect(url_for("login"))
    db.session.delete(FormData.query.get_or_404(entry_id))
    db.session.commit()
    return redirect(url_for("admin"))

# ---------- DB INIT ----------
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
