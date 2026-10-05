# src/analyzer.py
import sys
import logging
from pathlib import Path

import pandas as pd

# Добавляем корень проекта (родитель папки src) в путь поиска модулей,
# чтобы import config нашёл config.py в корне проекта
sys.path.insert(0, str(Path(__file__).parent.parent))

import config


class OrderAnalyzer:
    """Пакетный анализатор CSV-файлов с заказами."""

    def __init__(self):
        self.logger = self._setup_logger()
        self.stats = {
            "processed": 0,
            "errors": 0,
        }

    # ------------------------------------------------------------------
    # Инициализация логгера
    # ------------------------------------------------------------------
    def _setup_logger(self):
        """Настраивает логгер для записи ошибок в logs/errors.log."""
        config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger("OrderAnalyzer")
        logger.setLevel(logging.ERROR)

        # Чтобы не дублировать хендлеры при повторных вызовах
        if not logger.handlers:
            handler = logging.FileHandler(
                config.LOGS_DIR / config.LOG_FILENAME,
                mode="w",
                encoding="utf-8",
            )
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    # ------------------------------------------------------------------
    # Загрузка и валидация одного файла
    # ------------------------------------------------------------------
    def load_file(self, filepath: Path) -> pd.DataFrame:
        """Загружает один CSV и валидирует его структуру."""
        if not filepath.exists():
            raise FileNotFoundError(f"Файл не найден: {filepath}")

        if filepath.stat().st_size == 0:
            raise ValueError("Файл пустой")

        try:
            df = pd.read_csv(filepath)
        except pd.errors.ParserError as e:
            raise ValueError(f"Ошибка парсинга CSV: {e}")
        except Exception as e:
            raise ValueError(f"Не удалось прочитать файл: {e}")

        if df.empty:
            raise ValueError("В файле нет данных")

        # Проверка обязательных колонок
        missing = set(config.REQUIRED_COLUMNS) - set(df.columns)
        if missing:
            raise ValueError(f"Отсутствуют колонки: {missing}")

        # total_amount должен быть числовым
        df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")
        if df["total_amount"].isna().all():
            raise ValueError("Колонка total_amount не содержит чисел")

        return df

    # ------------------------------------------------------------------
    # Фильтрация доставленных заказов
    # ------------------------------------------------------------------
    def filter_delivered(self, df: pd.DataFrame) -> pd.DataFrame:
        """Оставляет только доставленные заказы."""
        return df[df[config.STATUS_COLUMN] == config.DELIVERED_STATUS]

    # ------------------------------------------------------------------
    # Расчёт метрик
    # ------------------------------------------------------------------
    def calculate_metrics(self, df: pd.DataFrame, filename: str) -> dict:
        """Считает метрики по отфильтрованному DataFrame."""
        return {
            "file": filename,
            "delivered_orders": len(df),
            "total_revenue": round(df["total_amount"].sum(), 2),
            "avg_order_value": round(df["total_amount"].mean(), 2)
                               if len(df) > 0 else 0.0,
        }

    # ------------------------------------------------------------------
    # Обработка одного файла
    # ------------------------------------------------------------------
    def process_file(self, filepath: Path):
        """Обрабатывает один файл. Возвращает метрики или None при ошибке."""
        try:
            df = self.load_file(filepath)
            delivered = self.filter_delivered(df)
            metrics = self.calculate_metrics(delivered, filepath.name)
            return metrics
        except Exception as e:
            self.stats["errors"] += 1
            msg = f"{filepath.name}: {type(e).__name__}: {e}"
            self.logger.error(msg)
            return None

    # ------------------------------------------------------------------
    # Обработка всех файлов в папке data/
    # ------------------------------------------------------------------
    def process_all(self) -> list:
        """Обрабатывает все CSV в data/ и сохраняет отчёт в reports/."""
        config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        files = sorted(config.DATA_DIR.glob("*.csv"))
        results = []

        for filepath in files:
            metrics = self.process_file(filepath)
            if metrics is not None:
                results.append(metrics)
                self.stats["processed"] += 1

        # Сохраняем отчёт, если есть успешные результаты
        if results:
            report_path = config.REPORTS_DIR / config.REPORT_FILENAME
            pd.DataFrame(results).to_csv(
                report_path, index=False, encoding="utf-8-sig"
            )

        return results
