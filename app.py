import os
from flask import Flask
from config import get_config
from models import db, login_manager


def create_app(config_class=None):
    app = Flask(__name__, instance_relative_config=True)

    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # Tự động tạo thư mục instance nếu chưa có
    import os
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from routes import register_blueprints
    register_blueprints(app)

    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    with app.app_context():
        db.create_all()
        print("✅ Database tables created.")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)