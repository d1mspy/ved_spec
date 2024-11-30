import sys
import sqlite3
from PyQt5 import QtWidgets,QtGui
from PyQt5.QtWidgets import QMessageBox


from persistent.game_class import Player, Enemy, Bullet, Ammo
# Импортировать наши классы игры
# from your_game_file import Game  # Импортируйте ваш класс Game из файла игры


class MainWindow( QtWidgets.QMainWindow ):
    def __init__(self):
        super( MainWindow,self ).__init__( )

        # Установка заголовка окна
        self.setWindowTitle( "Shooter Game" )
        self.setGeometry( 100,100,800,600 )  # (x, y, width, height)
        self.setWindowIcon( QtGui.QIcon( "path/to/icon.png" ) )  # Укажите путь к иконке

        # Создаем центральный виджет
        self.central_widget = QtWidgets.QWidget( self )
        self.setCentralWidget( self.central_widget )

        # Создание кнопок
        self.start_button = QtWidgets.QPushButton( "Начать новую игру",self.central_widget )
        self.start_button.setGeometry( 300,200,200,50 )
        self.start_button.clicked.connect( self.start_game )

        self.resume_button = QtWidgets.QPushButton( "Продолжить игру",self.central_widget )
        self.resume_button.setGeometry( 300,300,200,50 )
        self.resume_button.clicked.connect( self.resume_game )

        self.exit_button = QtWidgets.QPushButton( "Выход",self.central_widget )
        self.exit_button.setGeometry( 300,400,200,50 )
        self.exit_button.clicked.connect( self.close )

    def start_game(self):
        # Логика для запуска новой игры
        self.game = Game( )  # Замените текущим подходом для инициализации игры
        self.game.run( )  # Запуск метода run из вашего класса Game

    def resume_game(self):
        # Логика для возобновления игры
        QMessageBox.information( self,"Информация","Функция возобновления еще не реализована." )

    def display_scores(self):
        # Получение и отображение результатов из базы данных
        conn = sqlite3.connect( 'scores.db' )
        cursor = conn.cursor( )
        cursor.execute( 'SELECT name, score FROM scores ORDER BY score DESC LIMIT 10' )
        scores = cursor.fetchall( )
        conn.close( )

        scores_str = "\n".join( [f"{name}: {score}" for name,score in scores] )
        QMessageBox.information( self,"Топ-10 счетов",scores_str if scores_str else "Нет результатов." )


if __name__ == "__main__":
    app = QtWidgets.QApplication( sys.argv )
    window = MainWindow( )
    window.show( )
    sys.exit( app.exec_( ) )
