"""ثابت‌های متنی و وضعیتی پروژه.

این فایل برای متمرکز کردن رشته‌های تکراری، وضعیت‌ها و ایموجی‌ها ایجاد شد تا:
1. کاهش اشتباه تایپی
2. تسهیل تغییر/ترجمه آتی
3. یکنواختی پیام‌ها
"""

# وضعیت‌ها
STATUS_ENTERED = "وارد شده"
STATUS_EXITED = "خارج شده"

# ایموجی‌ها
EMOJI_SUCCESS = "✅"
EMOJI_ERROR = "❌"

# پیام‌های اعتبارسنجی و عملیات (قالب‌دار در صورت نیاز)
MSG_INVALID_NUMBER = f"شماره فاکتور نامعتبر است {EMOJI_ERROR}"
MSG_NOT_FOUND = "فاکتور {number} یافت نشد {error}"
MSG_ALREADY_REGISTERED_FORMAT = "فاکتور {number} ({date} - {time}) {status}"
MSG_REGISTERED = "فاکتور {number} ثبت شد {success}"
MSG_EXITED = "فاکتور {number} خارج شد {success}"
MSG_STATUS_UNKNOWN = "وضعیت نامشخص برای فاکتور {number} {error}"
MSG_CANNOT_DELETE_EXITED = "فاکتور {number} قبلاً خارج شده و قابل حذف نیست {error}"
MSG_DELETED = "فاکتور {number} حذف شد {success}"

# مجموعه‌ای از کاراکترهایی که ممکن است بعداً در تصمیم‌های UI استفاده شوند
SUCCESS_MARK = EMOJI_SUCCESS
ERROR_MARK = EMOJI_ERROR
