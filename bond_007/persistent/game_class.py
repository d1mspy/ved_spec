import pygame
import math
import random
from persistent.const import *

# Класс игрока
class Player :
    def __init__(self) :
        self.rect = pygame.Rect ( WIDTH // 2 , HEIGHT // 2 , 50 , 50 )
        self.health = MAX_HEALTH
        self.bullets = INITIAL_BULLETS

    def move(self , direction) :
        if direction == 'UP' and self.rect.top > 0 :
            self.rect.y -= PLAYER_SPEED
        if direction == 'DOWN' and self.rect.bottom < HEIGHT :
            self.rect.y += PLAYER_SPEED
        if direction == 'LEFT' and self.rect.left > 0 :
            self.rect.x -= PLAYER_SPEED
        if direction == 'RIGHT' and self.rect.right < WIDTH :
            self.rect.x += PLAYER_SPEED


# Класс врага
class Enemy :
    def __init__(self) :
        self.rect = pygame.Rect (random.randint ( 0 , WIDTH - 35 ) , random.randint ( 0 , HEIGHT - 35 ) , 35 , 35 )
        self.health = MAX_HEALTH
        self.last_shot_time = 0

    def move(self, player) :
        if self.rect.x < player.rect.x :
            self.rect.x += ENEMY_SPEED
        elif self.rect.x > player.rect.x :
            self.rect.x -= ENEMY_SPEED
        if self.rect.y < player.rect.y :
            self.rect.y += ENEMY_SPEED
        elif self.rect.y > player.rect.y :
            self.rect.y -= ENEMY_SPEED

    def shoot(self) :
        return Bullet ((self.rect.centerx, self.rect.centery), self.get_direction())

    def get_direction(self) :
        return (self.rect.x - WIDTH // 2 , self.rect.y - HEIGHT // 2)


# Класс пули
class Bullet :
    def __init__(self , pos , direction) :
        self.rect = pygame.Rect ( pos , (5 , 5) )
        angle = math.atan2 ( direction[1] , direction[0] )
        self.direction = (math.cos ( angle ) , math.sin ( angle ))

    def move(self) :
        self.rect.x += self.direction[0] * BULLET_SPEED
        self.rect.y += self.direction[1] * BULLET_SPEED


# Класс патронов
class Ammo :
    def __init__(self) :
        self.rect = pygame.Rect ( random.randint ( 0 , WIDTH - 20 ) , random.randint ( 0 , HEIGHT - 20 ) , 20 , 20 )