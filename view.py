# view.py

import sys
from datetime import timedelta

# وارد کردن کلاس‌های Qt در چند خط برای کوتاه شدن طول خطوط
from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QTableWidget,
    QSizePolicy,
    QSpacerItem,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QColor, QIcon
import jdatetime
from controller import Controller
import resources_rc  # pylint: disable=unused-import  # لازم برای ثبت ریسورس ها

# کلاس پنجره اصلی
class MainWindow(QMainWindow):  # pylint: disable=too-many-instance-attributes
    """پنجره اصلی برنامه مدیریت فاکتور."""

    def __init__(self) -> None:  # pylint: disable=too-many-instance-attributes
        super().__init__()
        self.controller = Controller()
        self._base_setup()
        self._setup_top_bar()
        self._setup_message_box()
        self._setup_mode_and_counter()
        self._setup_tables()
        self._setup_monthly_table()
        self._post_initialize()

    # ---------------------- setup sections ----------------------
    def _base_setup(self) -> None:
        self.setWindowTitle("مدیریت فاکتورها")
        self.setStyleSheet("background-color: white")
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_vertical_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_vertical_layout)

    def _setup_top_bar(self) -> None:
        self.first_horizontal_layout = QHBoxLayout()
        self.first_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.first_horizontal_layout.setSpacing(5)
        self.left_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.first_horizontal_layout.addItem(self.left_spacer)
        self.search_button = QPushButton()
        self.search_button.setIcon(QIcon(":/icons/search_icon.png"))
        self.search_button.setIconSize(QSize(32, 40))
        self.search_button.setStyleSheet("background-color: white; border: none;")
        self.first_horizontal_layout.addWidget(self.search_button)
        self.search_button.clicked.connect(self.handle_search)  # type: ignore[arg-type]
        self.barcode_input = QLineEdit()
        self.barcode_input.setMinimumSize(300, 40)
        self.barcode_input.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.barcode_input.setPlaceholderText("بارکد فاکتور را اسکن کنید")
        self.barcode_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.barcode_input.setStyleSheet(
            (
                "QLineEdit { background-color: white; color: black; font-size: 20px; "
                "border: 2px solid black; border-radius: 20px; padding: 0; selection-background-color: white; }"
                "QLineEdit:focus { border: 2px solid black; background-color: white; }"
                "QLineEdit:hover { border: 2px solid grey; }"
            )
        )
        self.first_horizontal_layout.addWidget(self.barcode_input)
        self.barcode_input.returnPressed.connect(self.handle_barcode)  # type: ignore[arg-type]
        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon(":/icons/trash_icon.png"))
        self.delete_button.setIconSize(QSize(32, 40))
        self.delete_button.setStyleSheet("background-color: white; border: none;")
        self.first_horizontal_layout.addWidget(self.delete_button)
        self.delete_button.clicked.connect(self.handle_delete)  # type: ignore[arg-type]
        self.right_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.first_horizontal_layout.addItem(self.right_spacer)
        self.main_vertical_layout.addLayout(self.first_horizontal_layout)

    def _setup_message_box(self) -> None:
        self.message_box = QLabel()
        self.message_box.setMinimumSize(0, 40)
        self.message_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_box.setStyleSheet(
            "background-color: white; color: black; font-size: 20px; border: 2px solid black; border-radius: 20px; padding: 0;"
        )
        self.main_vertical_layout.addWidget(self.message_box)
        self.message_timer = QTimer()
        self.message_timer.setSingleShot(True)
        self.message_timer.timeout.connect(self.clear_message_box)  # type: ignore[arg-type]

    def _setup_mode_and_counter(self) -> None:
        self.second_horizontal_layout = QHBoxLayout()
        self.exit_mode = QPushButton("حالت خروج", self)
        self.exit_mode.setCheckable(True)
        self.exit_mode.setMinimumSize(0, 40)
        self.exit_mode.setStyleSheet(
            """
            QPushButton { background-color: white; color: black; font-size: 20px; border: 2px solid black; border-radius: 20px; }
            QPushButton:checked { background-color: #06f500; color: black; border: 2px solid black; }
            """
        )
        self.second_horizontal_layout.addWidget(self.exit_mode)
        self.count_invoice_enter = QLabel()
        invoice_count = self.controller.get_count_invoice_enter()
        self.count_invoice_enter.setText(f"ورودی: {invoice_count}")
        self.count_invoice_enter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_invoice_enter.setFixedHeight(40)
        self.count_invoice_enter.setStyleSheet(
            "background-color: white; color: black; font-size: 20px; border: 2px solid black; border-radius: 20px; padding: 0;"
        )
        self.second_horizontal_layout.addWidget(self.count_invoice_enter)
        self.main_vertical_layout.addLayout(self.second_horizontal_layout)

    def _setup_tables(self) -> None:
        self.third_horizontal_layout = QHBoxLayout()
        # weekly table
        self.weekly_table = QTableWidget()
        self.weekly_table.setColumnCount(3)
        self.weekly_table.setRowCount(7)
        self.weekly_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.weekly_table.setHorizontalHeaderLabels(["خروجی", "ورودی", "تاریخ"])
        self.weekly_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.weekly_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.weekly_table.verticalHeader().setVisible(False)
        self.weekly_table.setAlternatingRowColors(True)
        self.weekly_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.weekly_table.setStyleSheet(
            (
                "QTableWidget { background-color: white; border: 2px solid black; border-radius: 20px; "
                "font-size: 20px; color: black; gridline-color: transparent; }"
                "QHeaderView::section { background-color: white; color: black; font-size: 20px; "
                "border-bottom: 2px solid black; }"
                "QTableWidget::item { border: none; padding: 10px; }"
                "QTableWidget::item:alternate { background-color: #bfbfbf; }"
            )
        )
        self.third_horizontal_layout.addWidget(self.weekly_table)
        # invoice table
        self.invoice_table = QTableWidget()
        self.invoice_table.setColumnCount(4)
        self.invoice_table.setHorizontalHeaderLabels(["خروج", "ساعت", "تاریخ", "شماره فاکتور"])
        self.invoice_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.invoice_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invoice_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.invoice_table.verticalHeader().setVisible(False)
        self.invoice_table.setAlternatingRowColors(True)
        self.invoice_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.invoice_table.setStyleSheet(
            (
                "QTableWidget { background-color: white; border: 2px solid black; border-radius: 20px; "
                "font-size: 20px; color: black; gridline-color: transparent; }"
                "QHeaderView::section { background-color: white; color: black; font-size: 20px; "
                "border-bottom: 2px solid black; }"
                "QTableWidget::item { border: none; padding: 10px; }"
                "QTableWidget::item:selected { background-color: #d1ffd6; color: black; }"
                "QTableWidget::item:alternate { background-color: #bfbfbf; }"
            )
        )
        self.third_horizontal_layout.addWidget(self.invoice_table)
        self.main_vertical_layout.addLayout(self.third_horizontal_layout)

    def _setup_monthly_table(self) -> None:
        self.monthly_table = QTableWidget()
        self.monthly_table.setRowCount(2)
        self.monthly_table.setColumnCount(31)
        self.monthly_table.setVerticalHeaderLabels(["تاریخ", "تعداد"])
        self.monthly_table.setFixedHeight(64)
        self.monthly_table.setAlternatingRowColors(True)
        for col in range(31):
            date_item = QTableWidgetItem(str(col + 1))
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.monthly_table.setItem(0, col, date_item)
            count_item = QTableWidgetItem("")
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.monthly_table.setItem(1, col, count_item)
        self.monthly_table.setStyleSheet(
            (
                "QTableWidget { background-color: white; border: 2px solid black; border-radius: 20px; "
                "font-size: 14px; color: black; gridline-color: transparent; }"
                "QHeaderView::section { background-color: white; color: black; font-size: 15px; "
                "border-bottom: 2px solid black; }"
                "QTableWidget::item { border: none; padding: 10px; }"
                "QTableWidget::item:selected { background-color: #d1ffd6; color: black; }"
                "QTableWidget::item:alternate { background-color: #bfbfbf; }"
            )
        )
        self.monthly_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.monthly_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.monthly_table.horizontalHeader().setVisible(False)
        self.monthly_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.main_vertical_layout.addWidget(self.monthly_table)

    def _post_initialize(self) -> None:
        self.barcode_input.setFocus()
        self.update_invoice_table()
        self.update_weekly_table()
        self.update_monthly_table()

    # عملگر اینتر برای کادر ثبت
    def handle_barcode(self):
        barcode = self.barcode_input.text().strip()

        if self.exit_mode.isChecked():
            message = self.controller.process_exit_invoice(barcode)
        else:
            message = self.controller.add_invoice(barcode)

        self.message_box.setText(message)
        count = self.controller.get_count_invoice_enter()
        self.count_invoice_enter.setText(f"ورودی: {count}")

        if "✅" in message:
            self.message_box.setStyleSheet(
                """
                background-color: #06f500;
                color: black;
                font-size: 20px;
                border: 2px solid black;
                border-radius: 20px;
                padding: 0px 0px;
                """
            )
        elif "❌" in message:
            self.message_box.setStyleSheet("""
                background-color: red;
                color: black;
                font-size: 20px;
                border: 2px solid black;
                border-radius: 20px;
                padding: 0px 0px;
            """)
        else:
            self.message_box.setStyleSheet(
                """
                background-color: #fffd3d;
                color: black;
                font-size: 20px;
                border: 2px solid black;
                border-radius: 20px;
                padding: 0px 0px;
                """
            )
        self.update_invoice_table()
        self.update_weekly_table()
        self.update_monthly_table()
        self.message_timer.start(10000)
        self.barcode_input.clear()

    # پاک کردن کادر پیام
    def clear_message_box(self):
        self.message_box.setText("")
        self.message_box.setStyleSheet("""
            background-color: white;
            color: black;
            font-size: 20px;
            border: 2px solid black;
            border-radius: 20px;
            padding: 0px 0px;
        """)

    # به روز رسانی جدول فاکتور ها
    def update_invoice_table(self):
        self.invoice_table.setRowCount(0)
        invoices = self.controller.get_all_invoices()
        for row_index, (number, date, time, status) in enumerate(invoices):
            self.invoice_table.insertRow(row_index)

            # اگر فاکتور خارج شده بود، تاریخ خروج را نمایش بده
            if status == "خارج شده":
                # دریافت اطلاعات خروج از دیتابیس
                invoice_info = self.controller.db.get_invoice_info(str(number))
                if invoice_info and invoice_info[3]:  # date_exit
                    status_display = invoice_info[3]  # date_exit
                else:
                    status_display = status
            else:
                status_display = status

            status_item = QTableWidgetItem(status_display)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            time_item = QTableWidgetItem(time)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            date_item = QTableWidgetItem(date)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            number_item = QTableWidgetItem(str(number))
            number_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # اگر فاکتور خارج شده بود، رنگ قرمز شود
            if status == "خارج شده":
                status_item.setForeground(QColor("red"))
                number_item.setForeground(QColor("red"))

            self.invoice_table.setItem(row_index, 0, status_item)
            self.invoice_table.setItem(row_index, 1, time_item)
            self.invoice_table.setItem(row_index, 2, date_item)
            self.invoice_table.setItem(row_index, 3, number_item)

    # به روز رسانی جدول هفتگی
    def update_weekly_table(self):
        weekly_data = self.controller.get_weekly_data()
        self.weekly_table.setRowCount(0)

        today = jdatetime.datetime.now()
        dates = []
        for i in range(7):
            # تبدیل تاریخ جلالی به میلادی و کم کردن روز، سپس تبدیل مجدد به جلالی
            gdate = today.togregorian() - timedelta(days=i)
            date_fixed = jdatetime.datetime.fromgregorian(datetime=gdate)
            dates.append(date_fixed.strftime("%Y/%m/%d"))
        data_dict = {row[0]: row[1:] for row in weekly_data}

        for row_index, date in enumerate(dates):
            self.weekly_table.insertRow(row_index)

            count_enter = data_dict.get(date, [0, 0])[0]
            count_exit = data_dict.get(date, [0, 0])[1]

            exit_item = QTableWidgetItem(str(count_exit))
            exit_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.weekly_table.setItem(row_index, 0, exit_item)

            enter_item = QTableWidgetItem(str(count_enter))
            enter_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.weekly_table.setItem(row_index, 1, enter_item)

            if row_index == 0:
                date_text = "امروز"
            elif row_index == 1:
                date_text = "دیروز"
            else:
                date_text = date

            date_item = QTableWidgetItem(date_text)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.weekly_table.setItem(row_index, 2, date_item)

    # به روز رسانی جدول ماهانه
    def update_monthly_table(self):
        monthly_data = self.controller.get_monthly_data()

        persian_months = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]

        current_month_number = jdatetime.datetime.now().month
        current_month_name = persian_months[current_month_number - 1]

        self.monthly_table.setVerticalHeaderLabels([current_month_name, "تعداد"])

        for col in range(31):
            count_item = QTableWidgetItem("")
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.monthly_table.setItem(1, col, count_item)

        for date, count in monthly_data:
            day = int(date.split("/")[-1])
            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.monthly_table.setItem(1, day - 1, count_item)

    # متد برای حذف فاکتور
    def handle_delete(self):
        invoice_number = self.barcode_input.text().strip()

        if not invoice_number.isdigit():
            self.message_box.setText("شماره فاکتور نامعتبر است ❌")
            self.message_box.setStyleSheet("""
                background-color: red;
                color: black;
                font-size: 20px;
                border: 2px solid black;
                border-radius: 20px;
            """)
            return

        result = self.controller.delete_invoice(invoice_number)
        self.message_box.setText(result)

        if "✅" in result:
            self.message_box.setStyleSheet("""
                background-color: #06f500;
                color: black;
                font-size: 20px;
                border: 2px solid black;
                border-radius: 20px;
            """)
        else:
            self.message_box.setStyleSheet("""
                background-color: red;
                color: black;
                font-size: 20px;
                border: 2px solid black;
                border-radius: 20px;
            """)

        # به‌روزرسانی جداول
        self.update_invoice_table()
        self.update_weekly_table()
        self.update_monthly_table()
        # به‌روزرسانی شمارش فاکتورهای ورودی
        count = self.controller.get_count_invoice_enter()
        self.count_invoice_enter.setText(f"ورودی: {count}")
        self.barcode_input.clear()
        self.barcode_input.setFocus()

    # متد برای جستجوی فاکتور
    def handle_search(self):
        invoice_number = self.barcode_input.text().strip()

        if not invoice_number.isdigit():
            self.message_box.setText("شماره فاکتور نامعتبر است ❌")
            self.message_box.setStyleSheet("""
                background-color: red;
                color: black;
                font-size: 20px;
                border: 2px solid black;
                border-radius: 20px;
            """)
            return

        invoice_details = self.controller.db.get_invoice_info(invoice_number)
        if invoice_details:
            date_enter, time_enter, first_status, date_exit, time_exit, second_status = invoice_details
            if second_status == "خارج شده":
                self.message_box.setText(f"فاکتور {invoice_number} ({date_exit} - {time_exit}) {second_status}")
            else:
                self.message_box.setText(f"فاکتور {invoice_number} ({date_enter} - {time_enter}) {first_status}")

            self.message_box.setStyleSheet("""
                background-color: #fffd3d;
                color: black;
                font-size: 20px;
                border: 2px solid black;
                border-radius: 20px;
            """)

        else:
            self.message_box.setText(f"فاکتور {invoice_number} یافت نشد ❌")
            self.message_box.setStyleSheet("""
                background-color: red;
                color: black;
                font-size: 20px;
                border: 2px solid black;
                border-radius: 20px;
            """)

        self.message_timer.start(10000)
        self.barcode_input.clear()
        self.barcode_input.setFocus()

# اجرای برنامه
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
