# Invoice management

[![CI](https://github.com/FarhadKhakzad/invoice-management/actions/workflows/ci.yml/badge.svg)](https://github.com/FarhadKhakzad/invoice-management/actions/workflows/ci.yml)

> Badge بالا بعد از اولین push و اجرای workflow به صورت خودکار وضعیت (passing/failing) را نمایش می‌دهد.

سیستم ساده مدیریت ورود/خروج فاکتور با رابط کاربری PySide6 و ذخیره سازی SQLite (تاریخ جلالی با jdatetime).

## ویژگی‌ها
- ثبت ورود فاکتور (زمان + تاریخ شمسی)
- ثبت خروج فاکتور و نمایش وضعیت قبلی
- شمارش لحظه‌ای فاکتورهای در وضعیت ورود
- گزارش هفتگی (ورود/خروج) و ماهانه (ورود روزانه)
- رابط کاربری ساده با PySide6
- تست‌های واحد (pytest) + pylint امتیاز 10/10

## نصب محلی
```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\pip install --upgrade pip
.venv\\Scripts\\pip install -r requirements.txt
.venv\\Scripts\\python view.py
```

## اجرای تست‌ها
```bash
.venv\\Scripts\\pytest -q
```

## اجرای pylint
```bash
.venv\\Scripts\\pylint controller.py model.py view.py constants.py tests
```

## پوشش (Coverage)
در CI اجرا می‌شود؛ محلی:
```bash
.venv\\Scripts\\coverage run -m pytest -q
.venv\\Scripts\\coverage report -m
```

## CI (GitHub Actions)
فایل Workflow در `.github/workflows/ci.yml`:
- Job lint: اجرای pylint
- Job tests: اجرای pytest + coverage (وابسته به lint)
- Job build-windows: ساخت exe با PyInstaller (Windows)
- Job build-linux: ساخت بسته (sdist, wheel)

Artifacts (خروجی‌ها) پس از اجرا در تب Actions قابل دانلود هستند.

## توسعه‌های آینده
- استخراج استایل‌ها به فایل QSS
- افزودن logging ساختاری
- افزودن گزینه export CSV
- فعال‌سازی mypy یا strict type check
- افزودن badge پوشش (Codecov)

## ساخت exe محلی
```bash
.venv\\Scripts\\pyinstaller invoice_management.spec --clean --noconfirm
```

## مجوز
(در صورت نیاز: MIT / Proprietary)
