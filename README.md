# Invoice management

[![CI](https://github.com/FarhadKhakzad/invoice-management/actions/workflows/ci.yml/badge.svg)](https://github.com/FarhadKhakzad/invoice-management/actions/workflows/ci.yml)
![Version](https://img.shields.io/github/v/tag/FarhadKhakzad/invoice-management?label=version&sort=semver)

> Badge بالا بعد از اولین push و اجرای workflow به صورت خودکار وضعیت (passing/failing) را نمایش می‌دهد.

> نسخه از تگ‌های Git خوانده می‌شود؛ با ساخت هر تگ جدید (مانند v0.1.1) badge به‌روز می‌شود.

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

## نسخه‌دهی (Versioning)
این پروژه از Semantic Versioning (الگوی MAJOR.MINOR.PATCH) و فایل `VERSION` به عنوان مرجع داخلی استفاده می‌کند:

1. فایل فعلی نسخه: `VERSION` (مقدار: 0.1.0)
2. تگ‌ها در Git باید با پیشوند v ساخته شوند (مانند: v0.1.0)
3. badge نسخه آخرین تگ semantic را نمایش می‌دهد.
4. برای به‌روزرسانی نسخه به صورت استاندارد از ابزار bump2version استفاده می‌کنیم.

### نصب ابزار نسخه‌دهی (اگر قبلاً نصب نشده)
در همان محیط venv:
```bash
pip install bump2version
```

یا چون در `requirements.txt` اضافه شده:
```bash
pip install -r requirements.txt
```

### دستورهای افزایش نسخه
```bash
# Patch (رفع باگ سازگار): x.y.z -> x.y.(z+1)
bump2version patch

# Minor (قابلیت جدید سازگار): x.y.z -> x.(y+1).0
bump2version minor

# Major (تغییر ناسازگار): x.y.z -> (x+1).0.0
bump2version major
```

هر دستور:
- فایل `VERSION` را به‌روز می‌کند
- Commit خودکار می‌سازد (Conventional Message)
- Tag جدید (مثلاً v0.1.1) ایجاد می‌کند

سپس push:
```bash
git push && git push --tags
```

### بررسی سلامت نسخه در CI
وقتی تگ push شود، مرحله Verify Version در CI بررسی می‌کند که محتوای فایل `VERSION` با تگ یکی باشد.

### به‌روزرسانی CHANGELOG
قبل از اجرای bump2version:
1. موارد جدید را از بخش Unreleased به بخش نسخه جدید منتقل کن
2. تاریخ را تنظیم کن (YYYY-MM-DD)
3. سپس bump2version اجرا کن

### سناریو نمونه
```bash
# بعد از چند fix و feature جدید:
vim CHANGELOG.md   # انتقال موارد به [0.2.0]
bump2version minor
git push && git push --tags
```

### نکته
اگر نمی‌خواهی هنوز release بدهی، فقط commit کن و bump2version اجرا نکن؛ badge همان نسخه قبلی را نشان می‌دهد.

## مجوز
(در صورت نیاز: MIT / Proprietary)
