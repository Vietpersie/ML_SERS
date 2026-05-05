import os
import json
import uuid
import pandas as pd
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from utils.helper import allowed_file, ensure_upload_folder
from utils.sers_processor import SERSProcessor

data_bp = Blueprint('data', __name__)


@data_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """Trang upload file CSV/Excel chứa dữ liệu SERS."""
    if request.method == 'GET':
        return render_template('data/upload.html', title='Upload dữ liệu SERS')

    # ── Kiểm tra file có được gửi lên không ──
    if 'file' not in request.files:
        flash('Chưa chọn file!', 'danger')
        return redirect(url_for('data.upload'))

    file = request.files['file']
    if file.filename == '':
        flash('Chưa chọn file!', 'danger')
        return redirect(url_for('data.upload'))

    if not allowed_file(file.filename):
        flash('Chỉ chấp nhận file .csv, .xlsx, .xls', 'danger')
        return redirect(url_for('data.upload'))

    # ── Lưu file ──
    folder = ensure_upload_folder()
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(folder, filename)
    file.save(filepath)

    # ── Xử lý dữ liệu ──
    processor = SERSProcessor(filepath)
    result = processor.process()

    if not result['success']:
        flash(f"Lỗi đọc file: {result['error']}", 'danger')
        return redirect(url_for('data.upload'))

    flash(f"Upload thành công! Đọc được {result['rows']} dòng dữ liệu.", 'success')
    return render_template(
        'data/preview.html',
        title='Xem trước dữ liệu',
        filename=file.filename,
        stats=result['stats'],
        preview=result['preview'],
        columns=result['columns'],
        file_id=filename,
    )


@data_bp.route('/api/data/<file_id>')
def get_data(file_id):
    """API trả về dữ liệu JSON để Plotly vẽ chart (Phase 3 sẽ dùng)."""
    # Bảo vệ: chỉ cho phép tên file hợp lệ
    if not file_id.replace('-', '').replace('.', '').replace('_', '').isalnum():
        return jsonify({'error': 'Invalid file id'}), 400

    folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    filepath = os.path.join(folder, file_id)

    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    processor = SERSProcessor(filepath)
    result = processor.process()

    if not result['success']:
        return jsonify({'error': result['error']}), 500

    return jsonify({
        'success': True,
        'data': result['chart_data'],
        'stats': result['stats'],
        'columns': result['columns'],
    })


@data_bp.route('/api/validate', methods=['POST'])
def validate_file():
    """API kiểm tra nhanh file trước khi upload (dùng cho JS)."""
    if 'file' not in request.files:
        return jsonify({'valid': False, 'error': 'No file'}), 400

    file = request.files['file']
    if not allowed_file(file.filename):
        return jsonify({'valid': False, 'error': 'Định dạng không hỗ trợ'}), 400

    return jsonify({'valid': True, 'filename': file.filename})
