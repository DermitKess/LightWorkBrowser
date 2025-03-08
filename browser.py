import os
import sys
from PyQt6.QtCore import QUrl, QDateTime, Qt, QStringListModel
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QToolBar, QToolButton, QMenu, QPushButton, QTableWidgetItem,
    QLabel, QComboBox, QFileDialog, QScrollArea, QListWidget, QListWidgetItem, QAbstractItemView
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest, QWebEnginePage
from datetime import datetime, timedelta

from widgets import CustomTabWidget
from utils import create_table, load_data, save_data, load_history, save_history

# Словарь переводов
translations = {
    "ru": {
        "History": "История",
        "Downloads": "Загрузки",
        "Settings": "Настройки",
        "Homepage": "Домашняя страница",
        "Localization": "Локализация",
        "Theme": "Тема",
        "Dark": "Темная",
        "Light": "Светлая",
        "Russian": "Русский",
        "English": "English",
        "Save Settings": "Сохранить настройки",
        "Close": "Закрыть",
        "New Tab": "Новая вкладка",
        "Search in History": "Поиск в истории",
        "Clear History": "Очистить историю",
        "History is empty": "История пуста",
        "Today": "Сегодня",
        "Yesterday": "Вчера",
        "Last 7 days": "Поиски за 7 дн.",
        "This month": "Этот месяц",
        "Old (6 months)": "Старые за 6 мес.",
        "Tags": "Метки",
        "January": "январь", "February": "февраль", "March": "март", "April": "апрель",
        "May": "май", "June": "июнь", "July": "июль", "August": "август",
        "September": "сентябрь", "October": "октябрь", "November": "ноябрь", "December": "декабрь",
        "Search in Downloads": "Поиск в загрузках",
        "Clear Downloads": "Очистить загрузки",
        "Downloads list is empty": "Список загрузок пуст",
        "Open Folder": "Открыть папку",
        "Save File As...": "Сохранить файл как...",
        "Back": "Назад",
        "Forward": "Вперед",
        "Reload": "Перезагрузить",
        "Copy": "Копировать",
        "Select All": "Выделить всё"
    },
    "en": {
        "History": "History",
        "Downloads": "Downloads",
        "Settings": "Settings",
        "Homepage": "Homepage",
        "Localization": "Localization",
        "Theme": "Theme",
        "Dark": "Dark",
        "Light": "Light",
        "Russian": "Russian",
        "English": "English",
        "Save Settings": "Save Settings",
        "Close": "Close",
        "New Tab": "New Tab",
        "Search in History": "Search in History",
        "Clear History": "Clear History",
        "History is empty": "History is empty",
        "Today": "Today",
        "Yesterday": "Yesterday",
        "Last 7 days": "Last 7 days",
        "This month": "This month",
        "Old (6 months)": "Old (6 months)",
        "Tags": "Tags",
        "January": "January", "February": "February", "March": "March", "April": "April",
        "May": "May", "June": "June", "July": "July", "August": "August",
        "September": "September", "October": "October", "November": "November", "December": "December",
        "Search in Downloads": "Search in Downloads",
        "Clear Downloads": "Clear Downloads",
        "Downloads list is empty": "Downloads list is empty",
        "Open Folder": "Open Folder",
        "Save File As...": "Save File As...",
        "Back": "Back",
        "Forward": "Forward",
        "Reload": "Reload",
        "Copy": "Copy",
        "Select All": "Select All"
    }
}

def translate(text, lang):
    return translations.get(lang, translations["ru"]).get(text, text)

class HistoryItem(QWidget):
    def __init__(self, title, url, visit_count=None, parent=None):
        super().__init__(parent)
        self.url = url
        self.parent_window = parent
        lang = self.parent().browser.settings_data.get("language", "ru")
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

        title_text = f"({visit_count}) {title}" if visit_count else title
        title_display = title_text[:40] + "..." if len(title_text) > 40 else title_text
        self.title_label = QLabel(f'<a href="{url}" style="color: inherit;"><b>{title_display}</b></a>')
        self.title_label.setOpenExternalLinks(False)
        # Удаляем setStyleSheet, стили будут задаваться через update_style
        self.title_label.linkActivated.connect(self.open_url)
        layout.addWidget(self.title_label)

        url_text = url[:40] + "..." if len(url) > 40 else url
        self.url_label = QLabel(url_text)
        # Удаляем setStyleSheet, стили будут задаваться через update_style
        layout.addWidget(self.url_label)

        self.setLayout(layout)
        self.update_style()  # Устанавливаем начальный стиль

    def update_style(self):
        theme = self.parent_window.browser.settings_data.get("theme", "dark")
        if theme == "dark":
            self.title_label.setStyleSheet("font-family: Manrope; font-size: 13px; color: #ffffff;")
            self.url_label.setStyleSheet("font-family: Manrope; font-size: 11px; color: #ffffff;")
        else:
            self.title_label.setStyleSheet("font-family: Manrope; font-size: 13px; color: #000000;")
            self.url_label.setStyleSheet("font-family: Manrope; font-size: 11px; color: #000000;")

    def mouseDoubleClickEvent(self, event):
        print(f"Double click on URL: {self.url}")
        browser = None
        if self.parent():
            parent = self.parent()
            while parent and not hasattr(parent, 'browser'):
                parent = parent.parent()
            if parent and hasattr(parent, 'browser'):
                browser = parent.browser
        if browser:
            print("Opening new tab...")
            browser.add_tab(self.url)
        else:
            print("Error: could not find browser object")
        event.accept()

    def open_url(self, url=None):
        print(f"Click on URL: {self.url}")
        browser = None
        if self.parent():
            parent = self.parent()
            while parent and not hasattr(parent, 'browser'):
                parent = parent.parent()
            if parent and hasattr(parent, 'browser'):
                browser = parent.browser
        if browser:
            print("Opening new tab...")
            browser.add_tab(self.url if url is None else url)
        else:
            print("Error: could not find browser object")

class HistoryWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browser = parent
        self.setWindowTitle(translate("History", self.browser.settings_data.get("language", "ru")))
        self.setGeometry(0, 0, 600, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(150)

        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        lang = self.browser.settings_data.get("language", "ru")
        categories = [
            translate("Today", lang),
            translate("Yesterday", lang),
            translate("Last 7 days", lang),
            translate("This month", lang)
        ]

        month_names = [
            translate("January", lang), translate("February", lang), translate("March", lang),
            translate("April", lang), translate("May", lang), translate("June", lang),
            translate("July", lang), translate("August", lang), translate("September", lang),
            translate("October", lang), translate("November", lang), translate("December", lang)
        ]
        for month in range(current_month - 1, 0, -1):
            categories.append(f"{month_names[month - 1]} {current_year}")

        categories.extend([translate("Old (6 months)", lang), translate("Tags", lang)])

        for category in categories:
            self.sidebar.addItem(QListWidgetItem(category))
        self.sidebar.itemClicked.connect(self.on_category_selected)
        main_layout.addWidget(self.sidebar)

        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)

        search_layout = QHBoxLayout()
        self.search_line_edit = QLineEdit()
        self.search_line_edit.setPlaceholderText(translate("Search in History", lang))
        self.search_line_edit.textChanged.connect(self.filter_history)
        self.clear_button = QPushButton(translate("Clear History", lang))
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        search_layout.addWidget(self.search_line_edit)
        search_layout.addWidget(self.clear_button)
        history_layout.addLayout(search_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.history_content = QWidget()
        self.history_layout = QVBoxLayout(self.history_content)
        self.history_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.history_layout.setContentsMargins(5, 5, 5, 5)
        self.history_layout.setSpacing(5)

        self.scroll_area.setWidget(self.history_content)
        history_layout.addWidget(self.scroll_area)

        main_layout.addWidget(history_widget)

        self.browser.history_data = load_history()
        self.update_history()
        self.update_theme()

        self.clear_button.clicked.connect(self.clear_history)

    def update_theme(self):
        theme = self.browser.settings_data.get("theme", "dark")
        if theme == "dark":
            self.setStyleSheet("""
            QWidget {background-color: #0e0e0e; color: #fff; font-family: Manrope; font-size: 13px;}
            QMainWindow {background-color: #0e0e0e;}
            QScrollArea {background-color: #0e0e0e; border: none;}
            QScrollBar:vertical, QScrollBar:horizontal {
                background-color: #000000;
                width: 10px;
                height: 10px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background-color: #2c2c2c;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                height: 0;
                width: 0;
            }
            QLineEdit {background-color: #000; color: #a5a5a5; padding: 5px; border-radius: 8px; font-family: Manrope; font-size: 13px; padding-bottom: 3px;}
            QPushButton {background-color: #2c2c2c; color: #fff; padding: 5px; border-radius: 8px; font-family: Manrope; font-size: 13px; border: none;}
            QPushButton:hover {background-color: #3c3c3c; border: 1px solid #373737;}
            QListWidget {background-color: #0e0e0e; color: #fff; border: none;}
            HistoryItem {background-color: #0e0e0e; border-bottom: 1px solid #202020;}
            """)
        else:
            self.setStyleSheet("""
            QWidget {background-color: #F5F5F5; color: #333333; font-family: Manrope; font-size: 13px;}
            QMainWindow {background-color: #F5F5F5;}
            QScrollArea {background-color: #FFFFFF; border: none; border-radius: 8px;}
            QScrollBar:vertical, QScrollBar:horizontal {
                background-color: #E0E0E0;
                width: 10px;
                height: 10px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background-color: #CCCCCC;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                height: 0;
                width: 0;
            }
            QLineEdit {background-color: #FFFFFF; color: #333333; padding: 5px; border-radius: 8px; font-family: Manrope; font-size: 13px; padding-bottom: 3px; border: 1px solid #CCCCCC;}
            QPushButton {background-color: #E0E0E0; color: #333333; padding: 5px; border-radius: 8px; font-family: Manrope; font-size: 13px; border: 1px solid #CCCCCC;}
            QPushButton:hover {background-color: #D1D1D1; border: 1px solid #BBBBBB; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
            QListWidget {background-color: #F5F5F5; color: #333333; border: none;}
            HistoryItem {background-color: #FFFFFF; border-bottom: 1px solid #E0E0E0; border-radius: 4px;}
            """)

    def on_category_selected(self, item):
        category = item.text()
        if not self.browser.history_data:
            self.update_history([])
            return

        current_date = datetime.now()
        filtered_data = []

        try:
            lang = self.browser.settings_data.get("language", "ru")
            for entry in self.browser.history_data:
                entry_date_str = entry.get("date", "")
                if not entry_date_str:
                    continue
                entry_date = datetime.strptime(entry_date_str, "%a %b %d %H:%M:%S %Y")

                if category == translate("Today", lang):
                    if entry_date.date() == current_date.date():
                        filtered_data.append(entry)
                elif category == translate("Yesterday", lang):
                    if entry_date.date() == (current_date - timedelta(days=1)).date():
                        filtered_data.append(entry)
                elif category == translate("Last 7 days", lang):
                    if (current_date - entry_date).days <= 7:
                        filtered_data.append(entry)
                elif category == translate("This month", lang):
                    if entry_date.month == current_date.month and entry_date.year == current_date.year:
                        filtered_data.append(entry)
                elif category == translate("Old (6 months)", lang):
                    if (current_date - entry_date).days > 180:
                        filtered_data.append(entry)
                elif category.endswith(str(current_date.year)):
                    month_map = {
                        translate("January", lang): 1, translate("February", lang): 2, translate("March", lang): 3,
                        translate("April", lang): 4, translate("May", lang): 5, translate("June", lang): 6,
                        translate("July", lang): 7, translate("August", lang): 8, translate("September", lang): 9,
                        translate("October", lang): 10, translate("November", lang): 11, translate("December", lang): 12
                    }
                    month_name = category.split()[0]
                    if month_name in month_map:
                        if entry_date.month == month_map[month_name] and entry_date.year == current_date.year:
                            filtered_data.append(entry)

        except Exception as e:
            print(f"Ошибка при фильтрации по категории: {e}")
            filtered_data = self.browser.history_data

        self.update_history(filtered_data)

    def update_history(self, history_data=None):
        for i in reversed(range(self.history_layout.count())):
            item = self.history_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        if history_data is None:
            history_data = self.browser.history_data

        if not history_data:
            empty_label = QLabel(translate("History is empty", self.browser.settings_data.get("language", "ru")))
            empty_label.setStyleSheet("font-family: Manrope; font-size: 13px;")
            self.history_layout.addWidget(empty_label)
            return

        history_dict = {}
        for entry in history_data:
            url = entry.get("url", "")
            if not url:
                continue
            if url in history_dict:
                history_dict[url]["count"] += 1
                history_dict[url]["title"] = entry["title"]
                history_dict[url]["date"] = entry["date"]
            else:
                history_dict[url] = {"title": entry["title"], "url": url, "date": entry["date"], "count": 1}

        sorted_entries = sorted(history_dict.values(), key=lambda x: x["date"], reverse=True)

        for entry in sorted_entries:
            try:
                item = HistoryItem(entry["title"], entry["url"], entry["count"], self)
                self.history_layout.addWidget(item)
            except Exception as e:
                print(f"Ошибка при добавлении элемента в историю: {e}")

    def filter_history(self, text):
        if not self.browser.history_data:
            self.update_history([])
            return

        filtered_data = [
            entry for entry in self.browser.history_data
            if text.lower() in entry.get("title", "").lower() or text.lower() in entry.get("url", "").lower()
        ]
        self.update_history(filtered_data)

    def clear_history(self):
        self.browser.history_data = []
        save_history(self.browser.history_data)
        self.update_history()

    def closeEvent(self, event):
        if self.browser and self in self.browser.history_windows:
            self.browser.history_windows.remove(self)
        event.accept()

class DownloadsItem(QWidget):
    def __init__(self, filename, path, parent=None):
        super().__init__(parent)
        self.filename = filename
        self.path = path if path and os.path.isabs(path) else "Unknown path"
        self.parent_window = parent
        lang = self.parent().browser.settings_data.get("language", "ru")
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

        self.file_label = QLabel(f'<a href="file:///{self.path}" style="color: inherit;"><b>{filename}</b></a>')
        self.file_label.setOpenExternalLinks(False)
        # Удаляем setStyleSheet, стили будут задаваться через update_style
        self.file_label.linkActivated.connect(self.open_file)
        self.file_label.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        layout.addWidget(self.file_label)

        path_text = self.path[:40] + "..." if len(self.path) > 40 else self.path
        self.path_label = QLabel(path_text)
        # Удаляем setStyleSheet, стили будут задаваться через update_style
        layout.addWidget(self.path_label)

        self.setLayout(layout)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.mousePressEvent = self.open_file_on_click

        self.update_style()  # Устанавливаем начальный стиль

    def update_style(self):
        theme = self.parent_window.browser.settings_data.get("theme", "dark")
        if theme == "dark":
            self.file_label.setStyleSheet("font-family: Manrope; font-size: 13px; color: #ffffff;")
            self.path_label.setStyleSheet("font-family: Manrope; font-size: 11px; color: #ffffff;")
        else:
            self.file_label.setStyleSheet("font-family: Manrope; font-size: 13px; color: #000000;")
            self.path_label.setStyleSheet("font-family: Manrope; font-size: 11px; color: #000000;")

    def open_file(self, path=None):
        path_to_open = self.path if path is None else path.replace("file:///", "")
        if os.path.exists(path_to_open) and path_to_open != "Unknown path":
            if sys.platform.startswith('win'):
                os.startfile(path_to_open)
            elif sys.platform.startswith('darwin'):
                os.system(f"open {path_to_open}")
            elif sys.platform.startswith('linux'):
                os.system(f"xdg-open {path_to_open}")
        else:
            print(f"Error: file not found at {path_to_open}")

    def open_file_on_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_file()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_file()
        event.accept()

    def show_context_menu(self, pos):
        lang = self.parent().browser.settings_data.get("language", "ru")
        menu = QMenu(self)
        open_folder_action = QAction(translate("Open Folder", lang), self)
        open_folder_action.triggered.connect(lambda: self.open_folder())
        menu.addAction(open_folder_action)
        menu.exec(self.mapToGlobal(pos))

    def open_folder(self):
        folder_path = os.path.dirname(self.path) if self.path != "Unknown path" else os.getcwd()
        if os.path.exists(folder_path):
            if sys.platform.startswith('win'):
                os.startfile(folder_path)
            elif sys.platform.startswith('darwin'):
                os.system(f"open {folder_path}")
            elif sys.platform.startswith('linux'):
                os.system(f"xdg-open {folder_path}")
        else:
            print(f"Error: folder not found at {folder_path}")

class DownloadsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browser = parent
        self.setWindowTitle(translate("Downloads", self.browser.settings_data.get("language", "ru")))
        self.setGeometry(0, 0, 600, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(150)

        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        lang = self.browser.settings_data.get("language", "ru")
        categories = [
            translate("Today", lang),
            translate("Yesterday", lang),
            translate("Last 7 days", lang),
            translate("This month", lang)
        ]

        month_names = [
            translate("January", lang), translate("February", lang), translate("March", lang),
            translate("April", lang), translate("May", lang), translate("June", lang),
            translate("July", lang), translate("August", lang), translate("September", lang),
            translate("October", lang), translate("November", lang), translate("December", lang)
        ]
        for month in range(current_month - 1, 0, -1):
            categories.append(f"{month_names[month - 1]} {current_year}")

        categories.extend([translate("Old (6 months)", lang), translate("Tags", lang)])

        for category in categories:
            self.sidebar.addItem(QListWidgetItem(category))
        self.sidebar.itemClicked.connect(self.on_category_selected)
        main_layout.addWidget(self.sidebar)

        downloads_widget = QWidget()
        downloads_layout = QVBoxLayout(downloads_widget)

        search_layout = QHBoxLayout()
        self.search_line_edit = QLineEdit()
        self.search_line_edit.setPlaceholderText(translate("Search in Downloads", lang))
        self.search_line_edit.textChanged.connect(self.filter_downloads)
        self.clear_button = QPushButton(translate("Clear Downloads", lang))
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        search_layout.addWidget(self.search_line_edit)
        search_layout.addWidget(self.clear_button)
        downloads_layout.addLayout(search_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.downloads_content = QWidget()
        self.downloads_layout = QVBoxLayout(self.downloads_content)
        self.downloads_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.downloads_layout.setContentsMargins(5, 5, 5, 5)
        self.downloads_layout.setSpacing(5)

        self.scroll_area.setWidget(self.downloads_content)
        downloads_layout.addWidget(self.scroll_area)

        main_layout.addWidget(downloads_widget)

        if not hasattr(self.browser, 'download_data'):
            self.browser.download_data = []
        self.update_downloads()

        self.update_theme()

        self.clear_button.clicked.connect(self.clear_downloads)

    def update_theme(self):
        theme = self.browser.settings_data.get("theme", "dark")
        if theme == "dark":
            self.setStyleSheet("""
            QWidget {background-color: #0e0e0e; color: #fff; font-family: Manrope; font-size: 13px;}
            QMainWindow {background-color: #0e0e0e;}
            QScrollArea {background-color: #0e0e0e; border: none;}
            QScrollBar:vertical, QScrollBar:horizontal {
                background-color: #000000;
                width: 10px;
                height: 10px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background-color: #2c2c2c;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                height: 0;
                width: 0;
            }
            QLineEdit {background-color: #000; color: #a5a5a5; padding: 5px; border-radius: 8px; font-family: Manrope; font-size: 13px; padding-bottom: 3px;}
            QPushButton {background-color: #2c2c2c; color: #fff; padding: 5px; border-radius: 8px; font-family: Manrope; font-size: 13px; border: none;}
            QPushButton:hover {background-color: #3c3c3c; border: 1px solid #373737;}
            QListWidget {background-color: #0e0e0e; color: #fff; border: none;}
            DownloadsItem {background-color: #0e0e0e; border-bottom: 1px solid #202020; color: #fff}
            """)
        else:
            self.setStyleSheet("""
            QWidget {background-color: #F5F5F5; color: #333333; font-family: Manrope; font-size: 13px;}
            QMainWindow {background-color: #F5F5F5;}
            QScrollArea {background-color: #FFFFFF; border: none; border-radius: 8px;}
            QScrollBar:vertical, QScrollBar:horizontal {
                background-color: #E0E0E0;
                width: 10px;
                height: 10px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background-color: #CCCCCC;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                height: 0;
                width: 0;
            }
            QLineEdit {background-color: #FFFFFF; color: #333333; padding: 5px; border-radius: 8px; font-family: Manrope; font-size: 13px; padding-bottom: 3px; border: 1px solid #CCCCCC;}
            QPushButton {background-color: #E0E0E0; color: #333333; padding: 5px; border-radius: 8px; font-family: Manrope; font-size: 13px; border: 1px solid #CCCCCC;}
            QPushButton:hover {background-color: #D1D1D1; border: 1px solid #BBBBBB; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
            QListWidget {background-color: #F5F5F5; color: #333333; border: none;}
            DownloadsItem {background-color: #FFFFFF; border-bottom: 1px solid #E0E0E0; border-radius: 4px;}
            """)

    def on_category_selected(self, item):
        category = item.text()
        if not self.browser.download_data:
            self.update_downloads([])
            return

        current_date = datetime.now()
        filtered_data = []

        try:
            lang = self.browser.settings_data.get("language", "ru")
            for entry in self.browser.download_data:
                entry_date_str = entry.get("date", "")
                if not entry_date_str:
                    continue
                # Пробуем разобрать дату в двух возможных форматах
                try:
                    entry_date = datetime.strptime(entry_date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        entry_date = datetime.strptime(entry_date_str, "%a %b %d %H:%M:%S %Y")
                    except ValueError as e:
                        print(f"Невозможно разобрать дату: {entry_date_str}, ошибка: {e}")
                        continue

                if category == translate("Today", lang):
                    if entry_date.date() == current_date.date():
                        filtered_data.append(entry)
                elif category == translate("Yesterday", lang):
                    if entry_date.date() == (current_date - timedelta(days=1)).date():
                        filtered_data.append(entry)
                elif category == translate("Last 7 days", lang):
                    if (current_date - entry_date).days <= 7:
                        filtered_data.append(entry)
                elif category == translate("This month", lang):
                    if entry_date.month == current_date.month and entry_date.year == current_date.year:
                        filtered_data.append(entry)
                elif category == translate("Old (6 months)", lang):
                    if (current_date - entry_date).days > 180:
                        filtered_data.append(entry)
                elif category.endswith(str(current_date.year)):
                    month_map = {
                        translate("January", lang): 1, translate("February", lang): 2, translate("March", lang): 3,
                        translate("April", lang): 4, translate("May", lang): 5, translate("June", lang): 6,
                        translate("July", lang): 7, translate("August", lang): 8, translate("September", lang): 9,
                        translate("October", lang): 10, translate("November", lang): 11, translate("December", lang): 12
                    }
                    month_name = category.split()[0]
                    if month_name in month_map:
                        if entry_date.month == month_map[month_name] and entry_date.year == current_date.year:
                            filtered_data.append(entry)

        except Exception as e:
            print(f"Ошибка при фильтрации по категории: {e}")
            filtered_data = self.browser.download_data

        self.update_downloads(filtered_data)

    def update_downloads(self, download_data=None):
        for i in reversed(range(self.downloads_layout.count())):
            item = self.downloads_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        if download_data is None:
            download_data = self.browser.download_data

        if not download_data:
            empty_label = QLabel(translate("Downloads list is empty", self.browser.settings_data.get("language", "ru")))
            empty_label.setStyleSheet("font-family: Manrope; font-size: 13px;")
            self.downloads_layout.addWidget(empty_label)
            return

        for entry in download_data:
            try:
                path = entry.get("path", "Unknown path")
                item = DownloadsItem(entry["filename"], path, self)
                self.downloads_layout.addWidget(item)
                item.update_style()  # Обновляем стиль каждого элемента
            except Exception as e:
                print(f"Ошибка при добавлении элемента загрузок: {e}")

    def filter_downloads(self, text):
        if not self.browser.download_data:
            self.update_downloads([])
            return

        filtered_data = [
            entry for entry in self.browser.download_data
            if text.lower() in entry.get("filename", "").lower() or text.lower() in entry.get("path", "").lower()
        ]
        self.update_downloads(filtered_data)

    def clear_downloads(self):
        self.browser.download_data = []
        self.browser.save_data()
        self.update_downloads()

    def closeEvent(self, event):
        if self.browser and self in getattr(self.browser, 'download_windows', []):
            self.browser.download_windows.remove(self)
        event.accept()

class SettingsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browser = parent
        self.setWindowTitle(translate("Settings", self.browser.settings_data.get("language", "ru")))
        self.setFixedSize(400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(10)

        homepage_label = QLabel(translate("Homepage", self.browser.settings_data.get("language", "ru")))
        self.homepage_edit = QLineEdit()
        self.homepage_edit.setText(self.browser.settings_data.get("homepage", "http://www.google.com"))
        layout.addWidget(homepage_label)
        layout.addWidget(self.homepage_edit)

        lang_label = QLabel(translate("Localization", self.browser.settings_data.get("language", "ru")))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem(translate("Russian", self.browser.settings_data.get("language", "ru")), "ru")
        self.lang_combo.addItem(translate("English", self.browser.settings_data.get("language", "ru")), "en")
        lang_value = self.browser.settings_data.get("language", "ru")
        index = self.lang_combo.findData(lang_value)
        if index != -1:
            self.lang_combo.setCurrentIndex(index)
        layout.addWidget(lang_label)
        layout.addWidget(self.lang_combo)

        theme_label = QLabel(translate("Theme", self.browser.settings_data.get("language", "ru")))
        self.theme_combo = QComboBox()
        self.theme_combo.addItem(translate("Dark", self.browser.settings_data.get("language", "ru")), "dark")
        self.theme_combo.addItem(translate("Light", self.browser.settings_data.get("language", "ru")), "light")
        theme_value = self.browser.settings_data.get("theme", "dark")
        index = self.theme_combo.findData(theme_value)
        if index != -1:
            self.theme_combo.setCurrentIndex(index)
        layout.addWidget(theme_label)
        layout.addWidget(self.theme_combo)

        button_layout = QHBoxLayout()
        save_button = QPushButton(translate("Save Settings", self.browser.settings_data.get("language", "ru")))
        save_button.clicked.connect(self.save_settings)
        close_button = QPushButton(translate("Close", self.browser.settings_data.get("language", "ru")))
        close_button.clicked.connect(self.close)
        button_layout.addWidget(save_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        self.update_theme()

    def update_theme(self):
        theme = self.browser.settings_data.get("theme", "dark")
        if theme == "dark":
            self.setStyleSheet("""
            QWidget {background-color: #0e0e0e; color: #fff; font-family: Manrope; font-size: 13px;}
            QMainWindow {background-color: #0e0e0e;}
            QLineEdit {background-color: #000; color: #a5a5a5; padding: 5px; border-radius: 8px; font-family: Manrope; font-size: 13px; padding-bottom: 3px;}
            QComboBox {background-color: #000; color: #a5a5a5; padding: 5px; border-radius: 8px;}
            QPushButton {background-color: #2c2c2c; color: #fff; padding: 5px; border-radius: 8px; font-family: Manrope; font-size: 13px; border: none;}
            QPushButton:hover {background-color: #3c3c3c; border: 1px solid #373737;}
            """)
        else:
            self.setStyleSheet("""
            QWidget {background-color: #F5F5F5; color: #333333; font-family: Manrope; font-size: 13px;}
            QMainWindow {background-color: #F5F5F5;}
            QLineEdit {background-color: #FFFFFF; color: #333333; padding: 5px; border-radius: 8px; font-family: Manrope; font-size: 13px; padding-bottom: 3px; border: 1px solid #CCCCCC;}
            QComboBox {background-color: #FFFFFF; color: #333333; padding: 5px; border-radius: 8px; border: 1px solid #CCCCCC;}
            QComboBox::drop-down {border: none;}
            QComboBox::down-arrow {image: url('assets/icons_light_theme/down_arrow.png'); width: 10px; height: 10px;}
            QPushButton {background-color: #E0E0E0; color: #333333; padding: 5px; border-radius: 8px; font-family: Manrope; font-size: 13px; border: 1px solid #CCCCCC;}
            QPushButton:hover {background-color: #D1D1D1; border: 1px solid #BBBBBB; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
            """)

    def save_settings(self):
        self.browser.settings_data["homepage"] = self.homepage_edit.text().strip() or "http://www.google.com"
        self.browser.settings_data["language"] = self.lang_combo.currentData()
        self.browser.settings_data["theme"] = self.theme_combo.currentData()
        self.browser.save_data()
        self.browser.apply_theme()
        self.update_language()
        self.close()

    def update_language(self):
        lang = self.browser.settings_data.get("language", "ru")
        self.setWindowTitle(translate("Settings", lang))
        self.findChildren(QLabel)[0].setText(translate("Homepage", lang))
        self.findChildren(QLabel)[1].setText(translate("Localization", lang))
        self.findChildren(QLabel)[2].setText(translate("Theme", lang))
        self.findChildren(QPushButton)[0].setText(translate("Save Settings", lang))
        self.findChildren(QPushButton)[1].setText(translate("Close", lang))
        self.lang_combo.clear()
        self.lang_combo.addItem(translate("Russian", lang), "ru")
        self.lang_combo.addItem(translate("English", lang), "en")
        lang_value = self.browser.settings_data.get("language", "ru")
        index = self.lang_combo.findData(lang_value)
        if index != -1:
            self.lang_combo.setCurrentIndex(index)
        self.theme_combo.clear()
        self.theme_combo.addItem(translate("Dark", lang), "dark")
        self.theme_combo.addItem(translate("Light", lang), "light")
        theme_value = self.browser.settings_data.get("theme", "dark")
        index = self.theme_combo.findData(theme_value)
        if index != -1:
            self.theme_combo.setCurrentIndex(index)

class BrowserTab(QWidget):
    def __init__(self, parent_browser, url=None):
        super().__init__()
        self.parent_browser = parent_browser
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        try:
            self.browser = QWebEngineView()
            self.url_bar = QLineEdit()
            self.url_bar.setPlaceholderText("Enter URL or search...")
            self.url_bar.returnPressed.connect(self.navigate_to_url)
            self.toolbar = QToolBar()
            self.toolbar2 = QToolBar()
            self.menu_button = None
            self.left_actions = []
            self.add_left_buttons()
            self.add_right_buttons()
            nav_layout = QHBoxLayout()
            nav_layout.setContentsMargins(0, 0, 0, 0)
            nav_layout.setSpacing(0)
            nav_layout.addWidget(self.toolbar)
            nav_layout.addWidget(self.url_bar)
            nav_layout.addWidget(self.toolbar2)
            self.layout().addLayout(nav_layout)
            self.layout().addWidget(self.browser)

            # Подключаем сигналы
            self.browser.titleChanged.connect(self.update_tab_title)
            self.browser.iconChanged.connect(self.update_tab_icon)
            self.browser.urlChanged.connect(self.update_url_bar)
            self.browser.loadFinished.connect(self.on_load_finished)
            self.browser.page().profile().downloadRequested.connect(self.handle_download)
            self.browser.loadFinished.connect(self.update_history)
            self.update_theme()

            # Загружаем URL, если он передан
            if url:
                validated_url = self.validate_url(url)
                print(f"Loading URL in BrowserTab: {validated_url}")  # Отладка
                self.url_bar.setText(validated_url)  # Устанавливаем URL в адресную строку
                self.browser.setUrl(QUrl.fromUserInput(validated_url))  # Используем QUrl.fromUserInput для надёжности

            print("BrowserTab initialized successfully")
        except Exception as e:
            print(f"Error initializing BrowserTab: {e}")
            import traceback
            traceback.print_exc()

    def validate_url(self, url):
        """Проверяет и корректирует URL, чтобы он был валидным."""
        url = str(url).strip()
        if not url:
            print("URL is empty, using default homepage")
            return "http://www.google.com"  # Если URL пустой, возвращаем домашнюю страницу
        if not url.startswith(("http://", "https://")):
            print(f"Adding http prefix to URL: {url}")
            url = "http://" + url
        return url

    def update_url_bar(self, qurl):
        """Обновляет адресную строку при изменении URL."""
        url = qurl.toString()
        print(f"URL changed to: {url}")  # Отладка
        if url != "about:blank":
            self.url_bar.setText(url)
        else:
            print("URL is about:blank, not updating URL bar")

    def on_load_finished(self, ok):
        """Обрабатывает завершение загрузки страницы."""
        if ok:
            print(f"Page loaded successfully: {self.browser.url().toString()}")
        else:
            print(f"Failed to load page: {self.browser.url().toString()}")

    def add_left_buttons(self):
        self.toolbar.clear()
        self.left_actions.clear()

        icon_folder = self.parent_browser.theme_icon_folder
        for icon, func in [("back", self.browser.back),
                           ("forward", self.browser.forward),
                           ("reload", self.browser.reload),
                           ("add", self.parent_browser.add_tab)]:
            icon_path = os.path.join(icon_folder, f"{icon}.png")
            if os.path.exists(icon_path):
                act = QAction(QIcon(icon_path), "", self)
            else:
                act = QAction("", self)
            act.triggered.connect(func)
            self.toolbar.addAction(act)
            self.left_actions.append(act)

    def add_right_buttons(self):
        self.toolbar2.clear()

        icon_folder = self.parent_browser.theme_icon_folder
        menu_icon_path = os.path.join(icon_folder, "menu.png")
        self.menu_button = QToolButton(self)
        if os.path.exists(menu_icon_path):
            self.menu_button.setIcon(QIcon(menu_icon_path))
        self.menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.menu_button.setMenu(self.create_menu())
        self.toolbar2.addWidget(self.menu_button)

    def create_menu(self):
        lang = self.parent_browser.settings_data.get("language", "ru")
        menu = QMenu(self)
        for text, slot in [(translate("Downloads", lang), self.parent_browser.open_downloads),
                           (translate("History", lang), self.parent_browser.open_history),
                           (translate("Settings", lang), self.parent_browser.open_settings)]:
            act = QAction(text, self)
            act.triggered.connect(slot)
            menu.addAction(act)
        return menu

    def update_theme(self):
        theme = self.parent_browser.settings_data.get("theme", "dark")
        icon_folder = self.parent_browser.theme_icon_folder

        for i, (icon, _) in enumerate([("back", self.browser.back),
                                       ("forward", self.browser.forward),
                                       ("reload", self.browser.reload),
                                       ("add", self.parent_browser.add_tab)]):
            if i < len(self.left_actions):
                icon_path = os.path.join(icon_folder, f"{icon}.png")
                if os.path.exists(icon_path):
                    self.left_actions[i].setIcon(QIcon(icon_path))
                else:
                    self.left_actions[i].setIcon(QIcon())

        menu_icon_path = os.path.join(icon_folder, "menu.png")
        if self.menu_button and os.path.exists(menu_icon_path):
            self.menu_button.setIcon(QIcon(menu_icon_path))

        if theme == "dark":
            self.url_bar.setStyleSheet(
                "QLineEdit {background-color:#000; color:#a5a5a5; padding: 5px; border-radius: 8px; font-family: Manrope; font-size: 13px; padding-bottom: 3px;}"
            )
            self.toolbar.setStyleSheet(
                "QToolBar {background-color:#0e0e0e; border:none; margin:0 5px; border-radius:8px;}"
                "QToolBar QToolButton {background-color:#0e0e0e; color:#fff; border:none; border-radius:8px;}"
                "QToolBar QToolButton:hover {background-color:#2c2c2c; border:1px solid #373737;}"
            )
            self.toolbar2.setStyleSheet(
                "QToolBar {background-color:#0e0e0e; border:none; margin:0 5px; border-radius:8px;}"
            )
            if self.menu_button:
                self.menu_button.setStyleSheet(
                    "QToolButton {background-color:#0e0e0e; color:#fff; border:none; border-radius:8px;}"
                    "QToolButton:hover {background-color:#2c2c2c; border:1px solid #373737;}"
                    "QToolButton::menu-indicator {image: none; width: 0;}"
                )
            menu = self.menu_button.menu()
            if menu:
                menu.setStyleSheet(
                    "QMenu {background-color:#101010; color:#fff; border:none; border-radius:4px; padding:6px;}"
                    "QMenu::item {padding:6px; border-radius:8px;}"
                    "QMenu::item:selected {background-color:#313131;}"
                )
        else:
            self.url_bar.setStyleSheet(
                "QLineEdit {background-color:#FFFFFF; color:#333333; padding: 5px; border-radius: 8px; font-family: Manrope; font-size: 13px; padding-bottom: 3px; border: 1px solid #CCCCCC;}"
            )
            self.toolbar.setStyleSheet(
                "QToolBar {background-color:#F5F5F5; border:none; margin:0 5px; border-radius:8px;}"
                "QToolBar QToolButton {background-color:#F5F5F5; color:#333333; border:none; border-radius:8px;}"
                "QToolBar QToolButton:hover {background-color:#E0E0E0; border:1px solid #CCCCCC;}"
            )
            self.toolbar2.setStyleSheet(
                "QToolBar {background-color:#F5F5F5; border:none; margin:0 5px; border-radius:8px;}"
            )
            if self.menu_button:
                self.menu_button.setStyleSheet(
                    "QToolButton {background-color:#F5F5F5; color:#333333; border:none; border-radius:8px;}"
                    "QToolButton:hover {background-color:#E0E0E0; border:1px solid #CCCCCC;}"
                    "QToolButton::menu-indicator {image: none; width: 0;}"
                )
            menu = self.menu_button.menu()
            if menu:
                menu.setStyleSheet(
                    "QMenu {background-color:#FFFFFF; color:#333333; border: 1px solid #CCCCCC; border-radius:4px; padding:6px;}"
                    "QMenu::item {padding:6px; border-radius:8px;}"
                    "QMenu::item:selected {background-color:#E0E0E0;}"
                )

    def update_tab_title(self, title):
        idx = self.parent_browser.tabs.indexOf(self)
        if idx != -1:
            self.parent_browser.tabs.setTabText(idx, title[:10])

    def update_tab_icon(self, icon):
        idx = self.parent_browser.tabs.indexOf(self)
        if idx != -1:
            self.parent_browser.tabs.setTabIcon(idx, icon)

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        print(f"Navigating to URL: {url}")  # Отладка
        if not url:
            print("URL is empty, navigation aborted")
            return
        if '.' not in url:
            url = f"https://www.google.com/search?q={url}"
            print(f"Converted to search URL: {url}")
        elif not url.startswith(("http://", "https://")):
            url = "http://" + url
            print(f"Added http prefix: {url}")
        try:
            self.url_bar.setText(url)  # Обновляем адресную строку перед загрузкой
            self.browser.setUrl(QUrl.fromUserInput(url))
        except Exception as e:
            print(f"Error setting URL: {e}")
            import traceback
            traceback.print_exc()

    def update_history(self, ok):
        if ok:
            try:
                title = self.browser.title()
                url = self.browser.url().toString()
                date = QDateTime.currentDateTime().toString()
                if title and url and url != "about:blank":
                    self.parent_browser.add_history_entry(title, url, date)
            except Exception as e:
                print(f"Ошибка истории: {e}")

    def handle_download(self, download: QWebEngineDownloadRequest):
        lang = self.parent_browser.settings_data.get("language", "ru")
        try:
            dlg = QFileDialog(self)
            dlg.setWindowTitle(translate("Save File As...", lang))
            dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            dlg.setDirectory(os.getcwd())
            dlg.setNameFilter("All files (*.*)")
            dlg.selectFile(download.downloadFileName())
            if dlg.exec():
                path = dlg.selectedFiles()[0]
                download.setDownloadDirectory(os.path.dirname(path))
                download.setDownloadFileName(os.path.basename(path))
                download.accept()
                date = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
                row = self.parent_browser.add_download_entry(os.path.basename(path), download.totalBytes(), path, date=date)
                download.finished.connect(lambda: self.parent_browser.update_download_status(row, "Completed"))
                print(f"Download started: {path}")
            else:
                download.cancel()
                print("Download canceled")
        except Exception as e:
            print(f"Ошибка загрузки: {e}")

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LightWork Browser")
        self.setGeometry(300, 300, 1280, 720)

        data = load_data()
        self.settings_data = data.get("settings", {
            "homepage": "http://www.google.com",
            "language": "ru",
            "theme": "dark"
        })
        self.theme_icon_folder = "assets/icons_dark_theme"
        self.tabs = CustomTabWidget(self, self.theme_icon_folder)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.tabs)

        self.history_data = load_history()
        self.download_data = data.get("downloads", [])
        self.history_windows = []
        self.settings_windows = []
        self.download_windows = []

        self.setup_tables()
        self.add_tab()
        self.apply_theme()

    def setup_tables(self):
        self.history_table = create_table(
            ["Website Name", "URL", "Visit Date"] if self.settings_data.get("language", "ru") == "en" else [
                "Название сайта", "Ссылка", "Дата посещения"])
        self.download_table = create_table(
            ["File Name", "Size", "Date", "Status"] if self.settings_data.get("language", "ru") == "en" else [
                "Имя файла", "Размер", "Дата", "Статус"])
        self.update_history_table()
        self.update_download_table()

    def setup_download_tab(self):
        downloads_tab = QWidget()
        downloads_tab.setLayout(QVBoxLayout())
        downloads_tab.layout().addWidget(self.download_table)
        self.update_download_table()
        lang = self.settings_data.get("language", "ru")
        self.tabs.add_tab(downloads_tab, translate("Downloads", lang))

    def setup_history_tab(self):
        history_tab = QWidget()
        history_tab.setLayout(QVBoxLayout())
        history_tab.layout().addWidget(self.history_table)
        self.update_history_table()
        lang = self.settings_data.get("language", "ru")
        self.tabs.add_tab(history_tab, translate("History", lang))

    def add_download_entry(self, filename, size, path, status=None, date=None):
        lang = self.settings_data.get("language", "ru")
        if status is None:
            status = "In progress" if lang == "en" else "В процессе"
        row = self.download_table.rowCount()
        self.download_table.insertRow(row)
        size_mb = f"{size / (1024 * 1024):.2f} MB" if size > 0 else "—"
        date_str = date or QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        for col, text in enumerate([filename, size_mb, date_str, status]):
            self.download_table.setItem(row, col, QTableWidgetItem(text))
        self.download_data.append({
            "filename": filename,
            "size": size_mb,
            "date": date_str,
            "status": status,
            "path": path
        })
        self.save_data()
        for window in self.download_windows:
            if window.isVisible():
                window.update_downloads()
        return row

    def update_download_status(self, row, status):
        if 0 <= row < self.download_table.rowCount():
            self.download_table.setItem(row, 3, QTableWidgetItem(status))
            self.download_data[row]["status"] = status
            self.save_data()
        for window in self.download_windows:
            if window.isVisible():
                window.update_downloads()

    def update_download_table(self):
        while self.download_table.rowCount():
            self.download_table.removeRow(0)
        for entry in self.download_data:
            row = self.download_table.rowCount()
            self.download_table.insertRow(row)
            for col, text in enumerate([entry["filename"], entry["size"], entry["date"], entry["status"]]):
                self.download_table.setItem(row, col, QTableWidgetItem(text))

    def update_history_table(self):
        while self.history_table.rowCount():
            self.history_table.removeRow(0)
        for entry in self.history_data:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            self.history_table.setItem(row, 0, QTableWidgetItem(entry["title"]))
            self.history_table.setItem(row, 1, QTableWidgetItem(entry["url"]))
            self.history_table.setItem(row, 2, QTableWidgetItem(entry["date"]))

    def add_history_entry(self, title, url, date):
        self.history_data.append({"title": title, "url": url, "date": date})
        save_history(self.history_data)
        self.update_history_table()
        for window in self.history_windows:
            if window.isVisible():
                window.update_history()

    def open_history(self):
        history_window = HistoryWindow(self)
        self.history_windows.append(history_window)
        history_window.show()

    def open_downloads(self):
        if not hasattr(self, 'download_windows'):
            self.download_windows = []
        downloads_window = DownloadsWindow(self)
        self.download_windows.append(downloads_window)
        downloads_window.show()

    def open_settings(self):
        settings_window = SettingsWindow(self)
        self.settings_windows.append(settings_window)
        settings_window.show()

    def apply_theme(self):
        if self.settings_data.get("theme", "dark") == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if isinstance(tab, BrowserTab):
                tab.update_theme()

        for window in self.history_windows:
            if window.isVisible():
                window.update_theme()
                window.update_history()

        for window in self.download_windows:
            if window.isVisible():
                window.update_theme()
                window.update_downloads()

        for window in self.settings_windows:
            if window.isVisible():
                window.update_theme()
                window.update_language()

    def add_tab(self, url=None):
        lang = self.settings_data.get("language", "ru")
        url = self.settings_data.get("homepage", "http://www.google.com")
        if url is None:
            url = self.settings_data.get("homepage", "http://www.google.com")
        print(f"Adding tab with URL: {url}")  # Отладка
        try:
            tab = BrowserTab(self, url)  # Передаём URL в конструктор BrowserTab
            idx = self.tabs.add_tab(tab, translate("New Tab", lang))
            self.tabs.setCurrentIndex(idx)
            print(f"New tab added at index {idx} with URL: {url}")
        except Exception as e:
            print(f"Error adding new tab: {e}")
            import traceback
            traceback.print_exc()

    def add_special_tab(self, title, tab_type):
        lang = self.settings_data.get("language", "ru")
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == translate(title, lang):
                self.tabs.setCurrentIndex(i)
                return
        if tab_type == "history":
            self.setup_history_tab()
        elif tab_type == "downloads":
            self.setup_download_tab()

    def save_data(self):
        data = {
            "downloads": self.download_data,
            "settings": self.settings_data
        }
        save_data(data)

    def closeEvent(self, event):
        self.save_data()
        save_history(self.history_data)
        event.accept()

    def apply_dark_theme(self):
        self.setStyleSheet("""
        QWidget {background-color:#0e0e0e; color:#fff; font-family:Manrope; font-size:13px; border:none; padding:0;}
        QTabWidget::pane {background-color:#0e0e0e; padding:0; margin:0;}
        QTabBar {background-color:#0e0e0e; padding:2px; margin:0;}
        QTabBar::tab {background-color:#0e0e0e; color:#fff; padding:5px; border-radius:8px; margin:4px;}
        QTabBar::tab:selected {background-color:#2c2c2c; border-radius:8px;}
        QTabBar::tab:hover {background-color:#1e1e1e; border:0 solid #373737;}
        QTabBar::close-button {
            image: url('assets/icons_dark_theme/close.png');
            width: 16px; height: 16px;
            background-color: transparent;
            border: none;
        }
        QTabBar::close-button:hover {
            image: url('assets/icons_dark_theme/close.png');
            background-color: #3c3c3c;
            border-radius: 4px;
        }
        QToolTip {background-color:#212121; color:#fff; font-size:13px; border:none; border-radius:8px; padding:2px; font-family:Manrope;}
        """)
        self.theme_icon_folder = "assets/icons_dark_theme"

    def apply_light_theme(self):
        self.setStyleSheet("""
        QWidget {background-color:#F5F5F5; color:#333333; font-family:Manrope; font-size:13px; border:none; padding:0;}
        QTabWidget::pane {background-color:#F5F5F5; padding:0; margin:0;}
        QTabBar {background-color:#F5F5F5; padding:2px; margin:0;}
        QTabBar::tab {background-color:#FFFFFF; color:#333333; padding:5px; border-radius:8px; margin:4px; border: 1px solid #CCCCCC; box-shadow: 0 1px 3px rgba(0,0,0,0.1);}
        QTabBar::tab:selected {background-color:#E0E0E0; border-radius:8px; border: 1px solid #CCCCCC;}
        QTabBar::tab:hover {background-color:#E8E8E8; border:1px solid #BBBBBB;}
        QTabBar::close-button {
            image: url('assets/icons_light_theme/close.png');
            width: 16px; height: 16px;
            background-color: transparent;
            border: none;
        }
        QTabBar::close-button:hover {
            image: url('assets/icons_light_theme/close.png');
            background-color: #D1D1D1;
            border-radius: 4px;
        }
        QToolTip {background-color:#FFFFFF; color:#333333; font-size:13px; border: 1px solid #CCCCCC; border-radius:8px; padding:2px; font-family:Manrope;}
        """)
        self.theme_icon_folder = "assets/icons_light_theme"