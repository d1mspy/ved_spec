import pygame  # type: ignore
from game import Game
from db.connect import check_table
from interface import interface

# функция запуска
if __name__ == "__main__":
    check_table()
    interface()
    Game().run()
    pygame.quit()
