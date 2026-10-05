# run.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import config
from src.analyzer import OrderAnalyzer


def main():
    analyzer = OrderAnalyzer()
    results = analyzer.process_all()

    print(f"📊 Обработано файлов: {analyzer.stats['processed']}")
    print(f"⚠️  Файлов с ошибками: {analyzer.stats['errors']}")
    print(f"📄 Отчёт: {config.REPORTS_DIR / config.REPORT_FILENAME}")
    print(f"📝 Лог:   {config.LOGS_DIR / config.LOG_FILENAME}")

    for r in results:
        print(f"  {r['file']}: заказов={r['delivered_orders']}, "
              f"выручка={r['total_revenue']}, "
              f"средний чек={r['avg_order_value']}")


if __name__ == "__main__":
    main()
