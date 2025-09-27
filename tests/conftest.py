import sqlite3
import pytest
from model import Database
from controller import Controller  # moved to top-level to satisfy pylint C0415


SCHEMA = """
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number INTEGER NOT NULL,
    date_enter TEXT NOT NULL,
    time_enter TEXT NOT NULL,
    first_status TEXT NOT NULL,
    date_exit TEXT,
    time_exit TEXT,
    second_status TEXT
);
"""


@pytest.fixture()
def memory_db(monkeypatch):  # noqa: D401
    """Provide an isolated in-memory Database instance.

    ترتیب مهم است:
    1. reset -> تضمین حذف singleton قبلی.
    2. ساخت instance (که به طور پیش‌فرض فایل invoices.db را باز می‌کند).
    3. بستن اتصال فایل و جایگزینی با :memory: (patch روی attribute های کلاس).
    4. ایجاد schema روی دیتابیس جدید.

    اگر قبل از ساخت instance پچ کنیم، __new__ اتصال ما را overwrite می‌کند.
    """
    Database.reset()
    instance = Database()  # اینجا singleton ساخته می‌شود (فایل واقعی)
    # بستن اتصال فایل و جایگزینی با in-memory
    try:
        instance.__class__.cursor.close()
    except Exception:  # pylint: disable=broad-except
        pass
    try:
        instance.__class__.connection.close()
    except Exception:  # pylint: disable=broad-except
        pass

    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.executescript(SCHEMA)
    conn.commit()
    monkeypatch.setattr(Database, "connection", conn, raising=False)
    monkeypatch.setattr(Database, "cursor", cursor, raising=False)
    yield instance
    # teardown
    try:
        cursor.close()
    finally:
        conn.close()
    Database.reset()


@pytest.fixture(name="app_controller")
def fixture_app_controller(request):  # noqa: D401
    """Controller using the isolated in-memory database without shadowing fixture name."""
    request.getfixturevalue("memory_db")  # ensure DB setup
    return Controller()


@pytest.fixture(name="add_sample_invoices")
def fixture_add_sample_invoices(request):  # noqa: D401
    """Populate sample invoices on isolated memory DB and return it (no name shadow)."""
    db: Database = request.getfixturevalue("memory_db")  # type: ignore[assignment]
    for number in ("100", "101", "102"):
        db.add_invoice(number)
    return db


def assert_message_pattern(message: str, contains: str, emoji: str | None = None) -> None:
    assert contains in message, f"'{contains}' not in '{message}'"
    if emoji:
        assert emoji in message, f"Emoji {emoji} missing in '{message}'"
