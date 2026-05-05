# Script fix tất cả file rỗng trong project
# Chạy: .\fix_empty_files.ps1

Write-Host "=== Bat dau fix cac file rong ===" -ForegroundColor Cyan

# ── models/__init__.py ──
Set-Content -Path "models\__init__.py" -Encoding UTF8 -Value @'
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Vui long dang nhap de tiep tuc.'
'@
Write-Host "[OK] models/__init__.py" -ForegroundColor Green

# ── models/user.py ──
Set-Content -Path "models\user.py" -Encoding UTF8 -Value @'
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, login_manager
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(64),  unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def __repr__(self):
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
'@
Write-Host "[OK] models/user.py" -ForegroundColor Green

# ── routes/__init__.py ──
Set-Content -Path "routes\__init__.py" -Encoding UTF8 -Value @'
from flask import Flask


def register_blueprints(app):
    from routes.home import home_bp
    from routes.auth import auth_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
'@
Write-Host "[OK] routes/__init__.py" -ForegroundColor Green

# ── routes/home.py ──
Set-Content -Path "routes\home.py" -Encoding UTF8 -Value @'
from flask import Blueprint, render_template

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    return render_template("index.html", title="ML-SERS Analyzer")


@home_bp.route("/about")
def about():
    return render_template("about.html", title="Gioi thieu")
'@
Write-Host "[OK] routes/home.py" -ForegroundColor Green

# ── routes/auth.py ──
Set-Content -Path "routes\auth.py" -Encoding UTF8 -Value @'
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
'@
Write-Host "[OK] routes/auth.py" -ForegroundColor Green

# ── utils/__init__.py ──
Set-Content -Path "utils\__init__.py" -Encoding UTF8 -Value "# Utils package"
Write-Host "[OK] utils/__init__.py" -ForegroundColor Green

# ── utils/helper.py ──
Set-Content -Path "utils\helper.py" -Encoding UTF8 -Value @'
import os
from flask import current_app


def allowed_file(filename):
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"csv", "xlsx", "xls"})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def ensure_upload_folder():
    folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


def human_readable_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / 1024 ** 2:.1f} MB"
'@
Write-Host "[OK] utils/helper.py" -ForegroundColor Green

# ── tests/__init__.py ──
Set-Content -Path "tests\__init__.py" -Encoding UTF8 -Value "# Tests package"
Write-Host "[OK] tests/__init__.py" -ForegroundColor Green

# ── tests/test_home.py ──
Set-Content -Path "tests\test_home.py" -Encoding UTF8 -Value @'
import pytest
from app import create_app
from config import TestingConfig


@pytest.fixture
def client():
    app = create_app(TestingConfig)
    with app.test_client() as client:
        yield client


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_about_page(client):
    response = client.get("/about")
    assert response.status_code == 200
'@
Write-Host "[OK] tests/test_home.py" -ForegroundColor Green

# ── tests/test_auth.py ──
Set-Content -Path "tests\test_auth.py" -Encoding UTF8 -Value @'
import pytest
from app import create_app
from config import TestingConfig
from models import db


@pytest.fixture
def client():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def test_login_page(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
'@
Write-Host "[OK] tests/test_auth.py" -ForegroundColor Green

Write-Host ""
Write-Host "=== Tat ca file da duoc fix! ===" -ForegroundColor Cyan
Write-Host "Chay tiep: python app.py" -ForegroundColor Yellow
