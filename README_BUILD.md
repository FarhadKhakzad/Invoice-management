# راهنمای ساخت (Build Guide)

## مشکل فعلی در Python 3.13
نسخه فعلی پایتون روی سیستم شما 3.13.7 است. پکیج PySide6 هنوز Wheel رسمی برای 3.13 منتشر نکرده و به همین دلیل هنگام اجرای برنامه‌ی فشرده‌شده (onefile) خطای `ModuleNotFoundError: No module named 'PySide6'` دریافت می‌شود.

PyInstaller در تحلیل سورس *وجود PySide6 را تشخیص می‌دهد* ولی چون ماژول واقعی (نصب شده) در محیط نیست، نمی‌تواند آن را Bundle کند؛ نتیجه: فایل اجرایی به ظاهر ساخته می‌شود ولی در اجرا (Runtime) کرش خاموش یا خطای صریح در نسخه Debug می‌دهد.

## راه‌حل سریع
یک محیط پایتون 3.12 یا 3.11 بساز، وابستگی‌ها را نصب کن، سپس بیلد کن.

### 1. نصب Python 3.12
از سایت python.org نسخه Windows 3.12.x (64-bit) را دانلود و نصب کن. هنگام نصب:
- گزینه "Add Python to PATH" را تیک بزن.

### 2. ساخت Virtual Environment (پیشنهادی)
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```
(اگر خطای ExecutionPolicy داشتی: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)

### 3. نصب وابستگی‌ها
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. تست اجرای مستقیم
```powershell
python view.py
```
اگر پنجره بدون خطا باز شد، ادامه بده.

### 5. ساخت نسخه onedir (پوشه‌ای)
```powershell
py -m PyInstaller --clean --noconfirm invoice_management.spec
```
خروجی: `dist/invoice_management/`

### 6. ساخت نسخه onefile (فشرده)
```powershell
py -m PyInstaller --clean --noconfirm invoice_management_onefile.spec
```
خروجی: `dist/invoice_management_onefile.exe`

### 7. افزودن آیکون (اختیاری)
یک فایل `app.ico` در مسیر `assets/` بساز (اگر وجود ندارد) و مقدار `ICON_PATH` را در spec تنظیم کن:
```python
ICON_PATH = str(BASE_DIR / 'assets' / 'app.ico')
```
سپس بیلد را تکرار کن.

### 8. دیباگ در صورت خطا
اگر نسخه onefile باز نشد:
```powershell
py -m PyInstaller --clean --noconfirm invoice_management_onefile_debug.spec
.\n# اجرای فایل:
.\n./dist/invoice_management_onefile_debug.exe
```
Traceback را بررسی کن.

## نکات حرفه‌ای
- بعد از اطمینان از پایداری، می‌توانی `PyInstaller==6.6.0` را ارتقا دهی؛ ولی ابتدا روی نسخه قفل شده تست کامل بگیر.
- برای جلوگیری از رشد فایل دیتابیس، می‌توان یک اسکریپت آرشیو ماهانه یا Vacuum دوره‌ای اضافه کرد.
- برای لاگ خطاهای Runtime (مثلاً Database Locked یا Permission): ماژول `logging` را اضافه کن و خطاها را در یک فایل مثل `logs/app.log` بنویس.

## جمع‌بندی
مشکل باز نشدن فایل onefile به دلیل نبودن PySide6 در محیط Python 3.13 است. با مهاجرت به Python 3.12 و نصب وابستگی‌ها، بیلد درست انجام می‌شود و exe به‌درستی اجرا خواهد شد.

---
هر زمان Python 3.13 به‌طور رسمی توسط PySide6 پشتیبانی شد، می‌توان نسخه‌ها را در `requirements.txt` به‌روزرسانی و دوباره تست کرد.
