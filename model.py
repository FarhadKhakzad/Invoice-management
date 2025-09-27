# model.py

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
import jdatetime

# کلاس اتصال به دیتابیس
class Database:
    """Singleton ساده برای مدیریت ارتباط با دیتابیس فاکتورها.

    یادداشت:
        - invoice_number در دیتابیس INTEGER است؛ در لایه بالاتر (controller) به صورت str ارسال می‌شود.
          SQLite تبدیل را خود انجام می‌دهد. برای یکپارچگی، پارامترها را str نگه می‌داریم و خروجی SELECT عددی می‌آید.
        - متدها مقادیر Optional برمی‌گردانند وقتی رکوردی وجود ندارد.
    """

    _instance: "Database | None" = None
    connection: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            # تعریف connection و cursor به صورت attribute شیء
            cls.connection = sqlite3.connect("invoices.db")
            cls.cursor = cls.connection.cursor()
            cls._instance.create_table()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton safely (for tests)."""
        if cls._instance is not None:
            try:
                cls.cursor.close()  # type: ignore[attr-defined]
            except Exception:  # pylint: disable=broad-except
                pass
            try:
                cls.connection.close()  # type: ignore[attr-defined]
            except Exception:  # pylint: disable=broad-except
                pass
        cls._instance = None
    # ایجاد جدول
    def create_table(self) -> None:
        query = """
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number INTEGER NOT NULL,
                date_enter TEXT NOT NULL,
                time_enter TEXT NOT NULL,
                first_status TEXT NOT NULL,
                date_exit TEXT,
                time_exit TEXT,
                second_status TEXT
            )
        """
        self.__class__.cursor.execute(query)
        self.__class__.connection.commit()

    # بررسی وجود فاکتور
    def invoice_exists(self, invoice_number: str) -> bool:
        """بررسی وجود فاکتور با شماره داده شده."""
        self.__class__.cursor.execute(
            "SELECT id FROM invoices WHERE invoice_number = ?", (invoice_number,)
        )
        return self.__class__.cursor.fetchone() is not None

    # ثبت فاکتور جدید
    def add_invoice(self, invoice_number: str) -> None:
        """افزودن فاکتور جدید در صورت نبود قبلی (ایگنور اگر موجود)."""
        if self.invoice_exists(invoice_number):
            return
        date = jdatetime.datetime.now().strftime("%Y/%m/%d")
        time = datetime.now().strftime("%H:%M:%S")
        self.__class__.cursor.execute("""
            INSERT INTO invoices (invoice_number, date_enter, time_enter, first_status) 
            VALUES (?, ?, ?, ?)
        """, (invoice_number, date, time, "وارد شده"))
        self.__class__.connection.commit()

    # دریافت زمان ثبت فاکتور وارد شده
    def get_invoice_enter(self, invoice_number: str) -> Optional[Tuple[str, str, str]]:
        """دریافت تاریخ/ساعت/وضعیت اولیه فاکتور (یا None)."""
        self.__class__.cursor.execute(
            "SELECT date_enter, time_enter, first_status FROM invoices WHERE invoice_number = ?",
            (invoice_number,),
        )
        return self.__class__.cursor.fetchone()
    # شمارش فاکتور های وارد شده
    def count_invoice_enter(self) -> int:
        """شمار فاکتورهای در وضعیت ورود (وارد شده)."""
        self.__class__.cursor.execute(
            "SELECT COUNT(*) FROM invoices WHERE first_status = 'وارد شده'"
        )
        return int(self.__class__.cursor.fetchone()[0])
    # ثبت خروج فاکتور
    def update_invoice_exit(self, invoice_number: str) -> None:
        date = jdatetime.datetime.now().strftime("%Y/%m/%d")
        time = datetime.now().strftime("%H:%M:%S")
        self.__class__.cursor.execute("""
            UPDATE invoices
            SET date_exit = ?, time_exit = ?, second_status = ?
            WHERE invoice_number = ? AND second_status IS NULL
        """, (date, time, "خارج شده", invoice_number))
        self.__class__.connection.commit()

    # دریافت وضعیت فاکتور
    def get_invoice_status(
        self, invoice_number: str
    ) -> Optional[Tuple[str, str, str, Optional[str], Optional[str], Optional[str]]]:
        """وضعیت کامل فاکتور یا None اگر وجود نداشته باشد."""
        self.__class__.cursor.execute(
            """
            SELECT date_enter, time_enter, first_status, date_exit, time_exit, second_status 
            FROM invoices WHERE invoice_number = ?
            """,
            (invoice_number,),
        )
        return self.__class__.cursor.fetchone()
    # دریافت اطلاعات کامل فاکتور
    def get_invoice_info(
        self, invoice_number: str
    ) -> Optional[Tuple[str, str, str, Optional[str], Optional[str], Optional[str]]]:
        """همان get_invoice_status (نام حفظ شده برای سازگاری)."""
        self.__class__.cursor.execute(
            """
            SELECT date_enter, time_enter, first_status, date_exit, time_exit, second_status 
            FROM invoices WHERE invoice_number = ?
            """,
            (invoice_number,),
        )
        return self.__class__.cursor.fetchone()

    # دریافت همه فاکتورها بر اساس زمان ثبت، از جدید به قدیم
    def get_all_invoices(self) -> List[Tuple[int, str, str, str]]:
        """لیست همه فاکتورها: (invoice_number, date_enter, time_enter, status)."""
        type(self).cursor.execute(
            """
            SELECT invoice_number, date_enter, time_enter,
                   CASE WHEN second_status IS NOT NULL THEN second_status ELSE first_status END AS status
            FROM invoices
            ORDER BY date_enter DESC, time_enter DESC
            """
        )
        rows_raw = type(self).cursor.fetchall()
        rows: List[Tuple[int, str, str, str]] = [
            (int(r[0]), str(r[1]), str(r[2]), str(r[3])) for r in rows_raw
        ]
        return rows
    # دریافت فاکتور ها برای جدول هفتگی
    def get_weekly_summary(self) -> List[Tuple[str, int, int]]:
        today = jdatetime.datetime.now().strftime("%Y/%m/%d")
        gdate = jdatetime.datetime.now().togregorian() - timedelta(days=7)
        one_week_ago = jdatetime.datetime.fromgregorian(datetime=gdate).strftime("%Y/%m/%d")
        type(self).cursor.execute(
            """
            SELECT date_enter, 
                SUM(CASE WHEN first_status = 'وارد شده' THEN 1 ELSE 0 END) as count_enter,
                SUM(CASE WHEN second_status = 'خارج شده' THEN 1 ELSE 0 END) as count_exit
            FROM invoices
            WHERE date_enter BETWEEN ? AND ?
            GROUP BY date_enter
            ORDER BY date_enter DESC
            """,
            (one_week_ago, today),
        )
        rows_raw = type(self).cursor.fetchall()
        rows: List[Tuple[str, int, int]] = [
            (str(r[0]), int(r[1]), int(r[2])) for r in rows_raw
        ]
        return rows
    # دریافت خلاصه داده‌های ماهانه
    def get_monthly_summary(self) -> List[Tuple[str, int]]:
        current_month = jdatetime.datetime.now().strftime("%Y/%m")
        type(self).cursor.execute(
            """
            SELECT date_enter, COUNT(*) as count_enter
            FROM invoices
            WHERE date_enter LIKE ?
            GROUP BY date_enter
            ORDER BY date_enter ASC
            """,
            (f"{current_month}%",),
        )
        rows_raw = type(self).cursor.fetchall()
        rows: List[Tuple[str, int]] = [
            (str(r[0]), int(r[1])) for r in rows_raw
        ]
        return rows
    # حذف فاکتور از دیتابیس
    def delete_invoice(self, invoice_number: str) -> bool:
        """حذف فاکتور اگر در وضعیت خروج نهایی نباشد."""
        status = self.get_invoice_status(invoice_number)
        if status:
            _, _, _, _, _, second_status = status
            if second_status == "خارج شده":
                return False
        self.__class__.cursor.execute(
            "DELETE FROM invoices WHERE invoice_number = ?", (invoice_number,)
        )
        self.__class__.connection.commit()
        return True
