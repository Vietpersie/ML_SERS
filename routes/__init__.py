from flask import Flask


def register_blueprints(app):
    from routes.home import home_bp
    from routes.auth import auth_bp
    from routes.data import data_bp          # ← THÊM DÒNG NÀY

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(data_bp, url_prefix="/data")  # ← THÊM DÒNG NÀY