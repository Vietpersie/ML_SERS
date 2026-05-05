from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Dang nhap thanh cong!", "success")
            return redirect(url_for("home.index"))
        flash("Sai ten dang nhap hoac mat khau.", "danger")

    return render_template("auth/login.html", title="Dang nhap")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Da dang xuat.", "info")
    return redirect(url_for("home.index"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if User.query.filter_by(username=username).first():
            flash("Ten dang nhap da ton tai.", "danger")
            return redirect(url_for("auth.register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Dang ky thanh cong! Vui long dang nhap.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html", title="Dang ky", register=True)
