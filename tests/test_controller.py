from constants import (
    EMOJI_SUCCESS,
    EMOJI_ERROR,
    STATUS_EXITED,
)


def test_add_invoice_success(app_controller):
    msg = app_controller.add_invoice("200")
    assert "200" in msg
    assert EMOJI_SUCCESS in msg


def test_add_invoice_invalid(app_controller):
    msg = app_controller.add_invoice("ABC")
    assert EMOJI_ERROR in msg


def test_add_then_exit(app_controller):
    app_controller.add_invoice("201")
    exit_msg = app_controller.process_exit_invoice("201")
    assert "201" in exit_msg and EMOJI_SUCCESS in exit_msg
    # Second exit should show existing status (not success exit again)
    second = app_controller.process_exit_invoice("201")
    assert STATUS_EXITED in second


def test_exit_not_found(app_controller):
    msg = app_controller.process_exit_invoice("999")
    assert EMOJI_ERROR in msg


def test_delete_flow(app_controller):
    app_controller.add_invoice("300")
    del_msg = app_controller.delete_invoice("300")
    assert EMOJI_SUCCESS in del_msg


def test_delete_after_exit_forbidden(app_controller):
    app_controller.add_invoice("301")
    app_controller.process_exit_invoice("301")
    msg = app_controller.delete_invoice("301")
    assert EMOJI_ERROR in msg


def test_get_all_invoices(app_controller):
    app_controller.add_invoice("400")
    rows = app_controller.get_all_invoices()
    assert any(str(r[0]) == "400" for r in rows)
