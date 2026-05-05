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
