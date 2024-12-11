import pygame  # type: ignore
import math
import random
from persistent.const import *


# Класс игрока
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2 - 25, 50, 50)
        self.health = MAX_HEALTH
        self.bullets = INITIAL_BULLETS

    def move(self, direction, pause, d1):
        if not pause:
            if direction == 'UP' and self.rect.top > 0 and not d1:
                self.rect.y -= PLAYER_SPEED
            if direction == 'DOWN' and self.rect.bottom < HEIGHT and not d1:
                self.rect.y += PLAYER_SPEED
            if direction == 'LEFT' and self.rect.left > 0:
                self.rect.x -= PLAYER_SPEED
            if direction == 'RIGHT' and self.rect.right < WIDTH:
                self.rect.x += PLAYER_SPEED


# Класс врага
class Enemy:
    def __init__(self, inc: int, d1: bool):
        self.size = 30
        self.increasing = inc
        final_size = self.size + 5*self.increasing
        if not d1:
            self.rect = pygame.Rect(random.randint(
                0, WIDTH - final_size), random.randint(0, HEIGHT - final_size), final_size, final_size)
        elif random.choice([True, False]):
            self.rect = pygame.Rect(random.randint(
                0, 70), random.randint(WALLS_HEIGHT, 800 - WALLS_HEIGHT - final_size), final_size, final_size)
        else:
            self.rect = pygame.Rect(random.randint(
                730, WIDTH-final_size), random.randint(WALLS_HEIGHT, 800 - WALLS_HEIGHT - final_size), final_size, final_size)
        # Количество попаданий для уничтожения врага
        self.health = HITS_TO_KILL_ENEMY + self.increasing
        self.max_health = HITS_TO_KILL_ENEMY + self.increasing
        self.last_shot_time = 0

    def move(self, player: Player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        length = max(1, (dx**2 + dy**2)**0.5)
        self.rect.move_ip(dx / length * ENEMY_SPEED, dy / length * ENEMY_SPEED)

    def shoot(self, player: Player):
        return Bullet((self.rect.centerx, self.rect.centery), self.get_direction(player))

    def get_direction(self, player: Player):
        direction = (player.rect.centerx - self.rect.centerx,
                     player.rect.centery - self.rect.centery)
        return direction

    def draw_health(self, screen):
        # Полоса здоровья врага
        health_bar_width = 30
        health_bar_height = 5
        health_bar_pos = (self.rect.x + ((self.size + 5 *
                          self.increasing) - health_bar_width)/2, self.rect.y - 10)
        health_percentage = self.health / self.max_health
        health_color = GREEN if self.health > 0 else RED
        pygame.draw.rect(screen, RED, (
            # Фон полосы здоровья
            health_bar_pos[0], health_bar_pos[1], health_bar_width, health_bar_height))
        pygame.draw.rect(screen, health_color, (
            health_bar_pos[0], health_bar_pos[1], health_bar_width *
            health_percentage,
            health_bar_height))  # Полоса здоровья


# Класс пули
class Bullet:
    def __init__(self, pos, direction):
        self.rect = pygame.Rect(pos, (5, 5))
        angle = math.atan2(direction[1], direction[0])
        self.direction = (math.cos(angle), math.sin(angle))

    def move(self):
        self.rect.x += self.direction[0] * BULLET_SPEED
        self.rect.y += self.direction[1] * BULLET_SPEED


# Класс патронов
class Ammo:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(
            0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20)
