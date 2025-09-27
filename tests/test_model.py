import jdatetime
from model import Database


def test_add_and_count(memory_db: Database):
    assert memory_db.count_invoice_enter() == 0
    memory_db.add_invoice("1")
    assert memory_db.count_invoice_enter() == 1


def test_duplicate_add_does_not_increase(memory_db: Database):
    memory_db.add_invoice("2")
    memory_db.add_invoice("2")
    assert memory_db.count_invoice_enter() == 1


def test_exit_updates_status(memory_db: Database):
    memory_db.add_invoice("3")
    status_before = memory_db.get_invoice_status("3")
    assert status_before and status_before[5] is None
    memory_db.update_invoice_exit("3")
    status_after = memory_db.get_invoice_status("3")
    assert status_after and status_after[5] == "خارج شده"


def test_delete_before_exit(memory_db: Database):
    memory_db.add_invoice("4")
    assert memory_db.delete_invoice("4") is True
    assert memory_db.get_invoice_status("4") is None


def test_delete_after_exit_not_allowed(memory_db: Database):
    memory_db.add_invoice("5")
    memory_db.update_invoice_exit("5")
    assert memory_db.delete_invoice("5") is False


def test_weekly_summary_structure(add_sample_invoices: Database):
    weekly = add_sample_invoices.get_weekly_summary()
    # Ensure list of tuples (date_enter, count_enter, count_exit)
    assert all(len(row) == 3 for row in weekly)


def test_monthly_summary_includes_today(memory_db: Database):
    today = jdatetime.datetime.now().strftime("%Y/%m/%d")
    memory_db.add_invoice("6")
    month_rows = memory_db.get_monthly_summary()
    days = {r[0] for r in month_rows}
    assert today in days
