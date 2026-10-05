# config.py
from pathlib import Path

# Базовые пути
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Имя выходного файла
REPORT_FILENAME = "summary_report.csv"
LOG_FILENAME = "errors.log"

# Настройки фильтрации
STATUS_COLUMN = "status"
DELIVERED_STATUS = "Delivered"

# Обязательные колонки для валидации
REQUIRED_COLUMNS = [
    "order_id", "person_id", "order_date", "status",
    "total_amount", "currency", "payment_method",
    "shipping_method", "notes",
]
