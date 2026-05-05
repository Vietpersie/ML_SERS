import os
import pandas as pd
import numpy as np


class SERSProcessor:
    """
    Đọc, validate và xử lý dữ liệu SERS từ file CSV hoặc Excel.

    Định dạng file hỗ trợ:
      - Cột 1: Wavenumber (cm⁻¹)
      - Cột 2+: Intensity của từng mẫu
    """

    SUPPORTED_EXT = {'csv', 'xlsx', 'xls'}
    MAX_ROWS = 10_000

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.ext = filepath.rsplit('.', 1)[-1].lower()
        self.df: pd.DataFrame | None = None

    # ── Đọc file ──────────────────────────────────────────────────────────────

    def _read_file(self) -> pd.DataFrame:
        """Đọc CSV hoặc Excel, tự động detect delimiter."""
        if self.ext == 'csv':
            # Thử các delimiter phổ biến
            for sep in [',', ';', '\t', ' ']:
                try:
                    df = pd.read_csv(self.filepath, sep=sep, encoding='utf-8-sig')
                    if df.shape[1] >= 2:
                        return df
                except Exception:
                    continue
            raise ValueError("Không thể đọc file CSV. Kiểm tra định dạng dấu phân cách.")

        elif self.ext in {'xlsx', 'xls'}:
            return pd.read_excel(self.filepath, engine='openpyxl' if self.ext == 'xlsx' else None)

        raise ValueError(f"Định dạng .{self.ext} không được hỗ trợ.")

    # ── Validate ──────────────────────────────────────────────────────────────

    def _validate(self, df: pd.DataFrame) -> list[str]:
        """Trả về danh sách cảnh báo (warnings). Rỗng = OK."""
        warnings = []

        if df.shape[1] < 2:
            raise ValueError("File cần ít nhất 2 cột (Wavenumber + Intensity).")

        if df.shape[0] == 0:
            raise ValueError("File không có dữ liệu.")

        if df.shape[0] > self.MAX_ROWS:
            warnings.append(f"File có {df.shape[0]} dòng, chỉ xử lý {self.MAX_ROWS} dòng đầu.")

        # Kiểm tra cột wavenumber có phải số không
        first_col = pd.to_numeric(df.iloc[:, 0], errors='coerce')
        if first_col.isna().sum() > df.shape[0] * 0.1:
            warnings.append("Cột đầu tiên có nhiều giá trị không phải số — kiểm tra lại cột Wavenumber.")

        # Kiểm tra giá trị âm trong intensity
        numeric_cols = df.select_dtypes(include=[np.number])
        if (numeric_cols < 0).any().any():
            warnings.append("Phát hiện giá trị intensity âm — có thể cần baseline correction.")

        return warnings

    # ── Xử lý chính ───────────────────────────────────────────────────────────

    def process(self) -> dict:
        """
        Xử lý file và trả về dict kết quả:
        {
            success: bool,
            error: str | None,
            rows: int,
            columns: list,
            preview: list[dict],   # 10 dòng đầu cho bảng HTML
            stats: dict,           # thống kê mô tả
            chart_data: dict,      # dữ liệu cho Plotly (Phase 3)
        }
        """
        try:
            df = self._read_file()
            warnings = self._validate(df)

            # Giới hạn số dòng
            df = df.head(self.MAX_ROWS)

            # Ép kiểu số cho tất cả cột
            df = df.apply(pd.to_numeric, errors='coerce')
            df.dropna(how='all', inplace=True)

            # Đặt tên cột rõ ràng nếu thiếu
            cols = list(df.columns)
            if not any(str(c).lower() in ['wavenumber', 'raman shift', 'cm-1', 'cm⁻¹'] for c in cols):
                df.columns = ['Wavenumber (cm⁻¹)'] + [f'Sample_{i}' for i in range(1, len(cols))]

            wavenumber_col = df.columns[0]
            sample_cols = list(df.columns[1:])

            # ── Thống kê ──
            stats = {
                'rows': len(df),
                'samples': len(sample_cols),
                'wavenumber_min': round(float(df[wavenumber_col].min()), 2),
                'wavenumber_max': round(float(df[wavenumber_col].max()), 2),
                'warnings': warnings,
                'sample_names': sample_cols,
            }

            # Thống kê intensity từng mẫu
            sample_stats = []
            for col in sample_cols:
                sample_stats.append({
                    'name': str(col),
                    'min':  round(float(df[col].min()), 4),
                    'max':  round(float(df[col].max()), 4),
                    'mean': round(float(df[col].mean()), 4),
                    'std':  round(float(df[col].std()), 4),
                })
            stats['sample_stats'] = sample_stats

            # ── Dữ liệu cho Plotly ──
            chart_data = {
                'wavenumber': df[wavenumber_col].tolist(),
                'samples': {
                    str(col): df[col].tolist() for col in sample_cols
                }
            }

            # ── Preview 10 dòng đầu ──
            preview = df.head(10).fillna('').to_dict(orient='records')

            return {
                'success': True,
                'error': None,
                'rows': len(df),
                'columns': list(df.columns),
                'preview': preview,
                'stats': stats,
                'chart_data': chart_data,
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'rows': 0,
                'columns': [],
                'preview': [],
                'stats': {},
                'chart_data': {},
            }
