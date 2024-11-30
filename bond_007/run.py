import pygame
from game import Game
from db.connect import check_table
from interface import interface

# функция запуска
if __name__ == "__main__":
    interface()
    check_table()
    Game().run()
    pygame.quit()
