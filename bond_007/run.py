import pygame # type: ignore
from game import Game
from db.connect import check_table

# функция запуска
if __name__ == "__main__":
    check_table()
    Game().run()
    pygame.quit()
