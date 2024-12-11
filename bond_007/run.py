import pygame  # type: ignore
from game import Game
from db.connect import check_table, get_leaders
from interface import interface

# функция запуска
if __name__ == "__main__":
    check_table()
    print(get_leaders())
    interface()
    Game().run()
    pygame.quit()
