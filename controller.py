# controller.py
"""ماژول کنترلر: لایه منطق بین View و Model.

اصلاحات اعمال‌شده (۱۹ مورد حرفه‌ای سازی):
1. افزودن ماژول داک‌استرینگ.
2. افزودن تایپ‌هینت برای تمام متدهای عمومی.
3. استخراج رشته‌های تکراری و وضعیت‌ها به constants.py.
4. افزودن کلاس کمکی تایپی برای وضعیت فاکتور (NamedTuple).
5. اعتبارسنجی متمرکز شماره فاکتور (_is_valid_invoice_number).
6. تبدیل پیام‌سازی تکراری به متد خصوصی (_format_invoice_status_message).
7. یکسان‌سازی استفاده از ایموجی‌های موفقیت/خطا از constants.
8. کاهش تکرار لاجیک تشخیص «خارج شده».
9. مستندسازی (داک‌استرینگ) متدهای کلیدی.
10. افزودن روش محافظه‌کارانه در برابر None هنگام واکشی رکورد.
11. جداسازی منطق ثبت ورود و نمایش وضعیت قبلی.
12. افزودن نرمال‌سازی شماره فاکتور (_normalize_invoice_number) جهت آینده (مثلاً Trim / حذف کاراکتر اضافی).
13. ساده‌سازی شرط حذف با خروج زودهنگام (early return).
14. یکنواخت‌سازی قالب پیام‌ها (همه از constants).
15. آماده‌سازی برای قابلیت چندزبانه در آینده با متمرکز کردن متن‌ها.
16. کاهش وابستگی مستقیم به ساختار tuple با NamedTuple (مستندتر شدن کد).
17. بهبود خوانایی با اسم‌های واضح و تایپ برگردان.
18. امکان توسعه سریع‌تر تست واحد (کاهش رشته‌های هاردکد).
19. آماده‌سازی مرحله بعد برای افزودن لاگ یا اینترفیس مخزن (Repository Pattern).
"""

from __future__ import annotations

from typing import Optional, NamedTuple, Tuple, List, TypeAlias

from model import Database
from constants import (
    STATUS_ENTERED,
    STATUS_EXITED,
    EMOJI_SUCCESS,
    EMOJI_ERROR,
    MSG_INVALID_NUMBER,
    MSG_ALREADY_REGISTERED_FORMAT,
    MSG_REGISTERED,
    MSG_EXITED,
    MSG_NOT_FOUND,
    MSG_STATUS_UNKNOWN,
    MSG_CANNOT_DELETE_EXITED,
    MSG_DELETED,
)


class InvoiceStatus(NamedTuple):
    """ساختار تایپی وضعیت یک فاکتور (خواناتر از tuple خام)."""
    date_enter: str
    time_enter: str
    first_status: str
    date_exit: Optional[str]
    time_exit: Optional[str]
    second_status: Optional[str]

# Type aliases برای وضوح بیشتر
InvoiceNumber: TypeAlias = str
InvoiceInfoRow: TypeAlias = Tuple[str, str, str, Optional[str], Optional[str], Optional[str]]
InvoiceListRow: TypeAlias = Tuple[int, str, str, str]
WeeklyRow: TypeAlias = Tuple[str, int, int]
MonthlyRow: TypeAlias = Tuple[str, int]

# کلاس کنترلر
class Controller:
    """کنترلر بین لایه رابط کاربری و پایگاه داده.

    وظایف:
        - اعتبارسنجی ورودی
        - تبدیل داده خام دیتابیس به پیام
        - منطق ورود / خروج و حذف
    """

    def __init__(self) -> None:
        self.db = Database()

    def add_invoice(self, invoice_number: InvoiceNumber) -> str:
        """ثبت فاکتور جدید یا بازگرداندن وضعیت قبلی."""
        norm = self._normalize_invoice_number(invoice_number)
        if not self._is_valid_invoice_number(norm):
            return MSG_INVALID_NUMBER
        existing: Optional[InvoiceInfoRow] = self.db.get_invoice_info(norm)  # type: ignore[assignment]
        if existing is not None:
            date_enter, time_enter, first_status, date_exit, time_exit, second_status = existing
            status = InvoiceStatus(date_enter, time_enter, first_status, date_exit, time_exit, second_status)
            return self._format_invoice_status_message(norm, status)
        self.db.add_invoice(norm)
        return MSG_REGISTERED.format(number=norm, success=EMOJI_SUCCESS)

    def get_count_invoice_enter(self) -> int:
        """تعداد فاکتورهای در وضعیت ورود."""
        return self.db.count_invoice_enter()

    def process_exit_invoice(self, invoice_number: InvoiceNumber) -> str:
        """ثبت خروج اگر واجد شرایط باشد، یا نمایش وضعیت."""
        norm = self._normalize_invoice_number(invoice_number)
        if not self._is_valid_invoice_number(norm):
            return MSG_INVALID_NUMBER
        status_tuple: Optional[InvoiceInfoRow] = self.db.get_invoice_status(norm)  # type: ignore[assignment]
        if status_tuple is None:
            return MSG_NOT_FOUND.format(number=norm, error=EMOJI_ERROR)
        date_enter, time_enter, first_status, date_exit, time_exit, second_status = status_tuple
        status = InvoiceStatus(date_enter, time_enter, first_status, date_exit, time_exit, second_status)
        if status.second_status == STATUS_EXITED:
            return self._format_invoice_status_message(norm, status)
        if status.first_status == STATUS_ENTERED:
            self.db.update_invoice_exit(norm)
            return MSG_EXITED.format(number=norm, success=EMOJI_SUCCESS)
        return MSG_STATUS_UNKNOWN.format(number=norm, error=EMOJI_ERROR)

    def get_all_invoices(self) -> List[InvoiceListRow]:
        """همه فاکتورها (زمان نزولی)."""
        return self.db.get_all_invoices()  # type: ignore[return-value]

    def get_weekly_data(self) -> List[WeeklyRow]:
        """خلاصه هفتگی ورود/خروج."""
        return self.db.get_weekly_summary()  # type: ignore[return-value]

    def get_monthly_data(self) -> List[MonthlyRow]:
        """خلاصه ماهانه ورود."""
        return self.db.get_monthly_summary()  # type: ignore[return-value]

    def delete_invoice(self, invoice_number: InvoiceNumber) -> str:
        """حذف فاکتور اگر خارج نشده باشد."""
        norm = self._normalize_invoice_number(invoice_number)
        if not self._is_valid_invoice_number(norm):
            return MSG_INVALID_NUMBER
        if not self.db.invoice_exists(norm):
            return MSG_NOT_FOUND.format(number=norm, error=EMOJI_ERROR)
        status_tuple: Optional[InvoiceInfoRow] = self.db.get_invoice_status(norm)  # type: ignore[assignment]
        if status_tuple is not None:
            date_enter, time_enter, first_status, date_exit, time_exit, second_status = status_tuple
            status = InvoiceStatus(date_enter, time_enter, first_status, date_exit, time_exit, second_status)
            if status.second_status == STATUS_EXITED:
                return MSG_CANNOT_DELETE_EXITED.format(number=norm, error=EMOJI_ERROR)
        if self.db.delete_invoice(norm) is False:
            return MSG_CANNOT_DELETE_EXITED.format(number=norm, error=EMOJI_ERROR)
        return MSG_DELETED.format(number=norm, success=EMOJI_SUCCESS)

    # ---------------------- helpers ----------------------
    def _normalize_invoice_number(self, invoice_number: str) -> str:
        """نرمال‌سازی ورودی (امکان توسعه برای حذف کاراکترهای غیرعددی)."""
        return invoice_number.strip()

    def _is_valid_invoice_number(self, invoice_number: str) -> bool:
        """اعتبارسنجی ساده: فقط ارقام و حداقل طول 1."""
        return bool(invoice_number) and invoice_number.isdigit()

    def _format_invoice_status_message(self, number: InvoiceNumber, status: InvoiceStatus) -> str:
        """ساخت پیام قابل نمایش بر اساس وضعیت فعلی."""
        if status.second_status == STATUS_EXITED and status.date_exit and status.time_exit:
            return MSG_ALREADY_REGISTERED_FORMAT.format(
                number=number,
                date=status.date_exit,
                time=status.time_exit,
                status=status.second_status,
            )
        return MSG_ALREADY_REGISTERED_FORMAT.format(
            number=number,
            date=status.date_enter,
            time=status.time_enter,
            status=status.first_status,
        )
