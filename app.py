from flask import Flask, render_template, request, flash, redirect, url_for, session
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
    return render_template("index.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin":
            session["admin"] = True
            return redirect(url_for("admin"))
        flash("Neplatné údaje")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("index"))

@app.route("/admin")
def admin():
    if not require_admin():
        return redirect(url_for("login"))
    return render_template("admin.html", items=FormData.query.all())

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
