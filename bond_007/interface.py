import sys
import sqlite3
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMessageBox, QLabel, QVBoxLayout, QCheckBox
from PyQt5.QtGui import QFont, QPixmap
from game import Game


def interface() -> None:
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Установка заголовка окна
        self.setWindowTitle("Shooter Game")
        self.setGeometry(100, 100, 800, 600)  # (x, y, width, height)
        self.setWindowIcon(QtGui.QIcon("path/to/icon.png")
                           )  # Укажите путь к иконке

        # Создаем центральный виджет
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.label = QLabel(self)
        pixmap = QPixmap('bond_007\costyl.jpg')

        if pixmap.isNull():
            print("Ошибка: изображение не загружено.")
        else:
            self.label.setPixmap(pixmap)
            self.label.setScaledContents(True)

        self.layout.addWidget(self.label)

        font = QFont("Arial", 16)

        self.checkbox = QCheckBox("1D", self.central_widget)
        self.checkbox.setGeometry(1010, 70, 100, 100)
        self.checkbox.setFont(font)

        # Создание кнопок
        self.start_button = QtWidgets.QPushButton(
            "Начать новую игру", self.central_widget)
        self.start_button.setGeometry(700, 70, 300, 100)
        self.start_button.setFont(font)
        self.start_button.clicked.connect(self.start_game)

        self.resume_button = QtWidgets.QPushButton(
            "Продолжить игру", self.central_widget)
        self.resume_button.setGeometry(700, 180, 300, 100)
        self.resume_button.setFont(font)
        self.resume_button.clicked.connect(self.resume_game)

        self.exit_button = QtWidgets.QPushButton("Выход", self.central_widget)
        self.exit_button.setGeometry(700, 290, 300, 100)
        self.exit_button.setFont(font)
        self.exit_button.clicked.connect(self.close)

    def start_game(self):
        # Логика для запуска новой игры
        username, ok = QtWidgets.QInputDialog.getText(
            self, "Имя игрока", "Введите ваше имя:")
        if ok and username.strip():
            game = Game(username.strip(), self.checkbox.isChecked())
            game.run()
        else:
            QtWidgets.QMessageBox.warning(
                self, "Ошибка", "Имя не может быть пустым!")

    def resume_game(self):
        # Логика для возобновления игры
        QMessageBox.information(
            self, "Информация", "Функция возобновления еще не реализована.")

    def display_scores(self):
        # Получение и отображение результатов из базы данных
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT name, score FROM scores ORDER BY score DESC LIMIT 10')
        scores = cursor.fetchall()
        conn.close()

        scores_str = "\n".join([f"{name}: {score}" for name, score in scores])
        QMessageBox.information(
            self, "Топ-10 счетов", scores_str if scores_str else "Нет результатов.")
