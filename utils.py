import json
import os
from PyQt6.QtWidgets import QTableWidget, QHeaderView

TABLE_STYLE = """
QTableWidget { background-color: #101010; color: #fff; border: none; font-size: 13px; font-family: Manrope; }
QHeaderView::section { background-color: #202020; color: #fff; padding: 6px; border: none; border-bottom: 1px solid #373737; }
QTableWidget::item { padding: 6px; }
QTableWidget::item:selected { background-color: #373737; }
"""

HISTORY_FILE = os.path.join(os.getcwd(), "history.json")
DATA_FILE = os.path.join(os.getcwd(), "data.json")

def create_table(headers):
    table = QTableWidget()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.setStyleSheet(TABLE_STYLE)
    return table

def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"Загружена история из {HISTORY_FILE}: {data}")
                return data
        return []
    except Exception as e:
        print(f"Ошибка при загрузке истории: {e}")
        return []

def save_history(history_data):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=4)
        print(f"История сохранена в {HISTORY_FILE}: {history_data}")
    except Exception as e:
        print(f"Ошибка при сохранении истории: {e}")

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return {}

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")