# game.py
import pygame
import random
import math
import requests
from models import Score
from database import submit_score

# Константы
WIDTH , HEIGHT = 1000 , 800
PLAYER_SPEED = 5
ENEMY_SPEED = 2
BULLET_SPEED = 10
MAX_HEALTH = 100
INITIAL_BULLETS = 200
ENEMY_SPAWN_RATE = 3000  # milliseconds
ENEMY_HIT_DAMAGE = 10
BULLET_HIT_DAMAGE = 10
AMMO_SPAWN_RATE = 20000  # 20 seconds
ENEMY_COUNT_PER_WAVE = 3
WAVE_DELAY = 7000  # 7 seconds between waves


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
        self.rect = pygame.Rect ( random.randint ( 0 , WIDTH - 35 ) , random.randint ( 0 , HEIGHT - 35 ) , 35 , 35 )
        self.health = MAX_HEALTH
        self.last_shot_time = 0

    def move(self , player) :
        if self.rect.x < player.rect.x :
            self.rect.x += ENEMY_SPEED
        elif self.rect.x > player.rect.x :
            self.rect.x -= ENEMY_SPEED
        if self.rect.y < player.rect.y :
            self.rect.y += ENEMY_SPEED
        elif self.rect.y > player.rect.y :
            self.rect.y -= ENEMY_SPEED

    def shoot(self) :
        return Bullet ( (self.rect.centerx , self.rect.centery) , self.get_direction ( ) )

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


# Основная игра
class Game :
    def __init__(self) :
        pygame.init ( )
        self.screen = pygame.display.set_mode ( (WIDTH , HEIGHT) )
        pygame.display.set_caption ( "Shooter Game" )
        self.clock = pygame.time.Clock ( )
        self.player = Player ( )
        self.enemies = []
        self.bullets = []
        self.ammo = []
        self.score = 0
        self.enemy_spawn_timer = pygame.time.get_ticks ( )
        self.ammo_spawn_timer = pygame.time.get_ticks ( )
        self.wave_time = pygame.time.get_ticks ( )
        self.spawn_delay = ENEMY_SPAWN_RATE
        self.running = True
        self.game_over = False

    def run(self) :
        while self.running :
            self.handle_events ( )
            self.update ( )
            self.render ( )
            self.clock.tick ( 60 )

    def handle_events(self) :
        for event in pygame.event.get ( ) :
            if event.type == pygame.QUIT :
                self.running = False

        keys = pygame.key.get_pressed ( )
        if keys[pygame.K_UP] :
            self.player.move ( 'UP' )
        if keys[pygame.K_DOWN] :
            self.player.move ( 'DOWN' )
        if keys[pygame.K_LEFT] :
            self.player.move ( 'LEFT' )
        if keys[pygame.K_RIGHT] :
            self.player.move ( 'RIGHT' )
        if keys[pygame.K_SPACE] and self.player.bullets > 0 :
            mouse_x , mouse_y = pygame.mouse.get_pos ( )
            bullet_start_pos = (self.player.rect.centerx , self.player.rect.top)
            direction = (mouse_x - bullet_start_pos[0] , mouse_y - bullet_start_pos[1])
            bullet = Bullet ( bullet_start_pos , direction )
            self.bullets.append ( bullet )
            self.player.bullets -= 1

    def sync_score(self) :
        name = input ( "Enter your name: " )
        submit_score ( name , self.score )  # Сохраняем очки в базе данных

    def update(self) :
        for bullet in self.bullets[:] :
            bullet.move ( )
            if bullet.rect.bottom < 0 or bullet.rect.left < 0 or bullet.rect.right > WIDTH or bullet.rect.top > HEIGHT :
                self.bullets.remove ( bullet )

        for bullet in self.bullets[:] :
            for enemy in self.enemies[:] :
                if bullet.rect.colliderect ( enemy.rect ) :
                    enemy.health -= BULLET_HIT_DAMAGE
                    self.bullets.remove ( bullet )
                    if enemy.health <= 0 :
                        self.enemies.remove ( enemy )
                        self.score += 1
                    break

        for enemy in self.enemies :
            enemy.move ( self.player )
            if enemy.rect.colliderect ( self.player.rect ) :
                self.player.health -= ENEMY_HIT_DAMAGE
                if self.player.health <= 0 and not self.game_over :
                    print ( "Game Over! Final Score:" , self.score )
                    self.sync_score ( )
                    self.game_over = True
                    self.running = False

            current_time = pygame.time.get_ticks ( )
            if current_time - enemy.last_shot_time > 2000 :  # Враги стреляют каждые 2 секунды
                bullet = enemy.shoot ( )
                self.bullets.append ( bullet )
                enemy.last_shot_time = current_time

        current_time = pygame.time.get_ticks ( )
        if current_time - self.enemy_spawn_timer > self.spawn_delay :
            for _ in range ( ENEMY_COUNT_PER_WAVE ) :
                self.enemies.append ( Enemy ( ) )
            self.enemy_spawn_timer = current_time

        if current_time - self.wave_time > WAVE_DELAY :
            self.enemy_spawn_timer = current_time
            self.spawn_delay = max ( 1000 , self.spawn_delay - 100 )

        if current_time - self.ammo_spawn_timer > AMMO_SPAWN_RATE :
            self.ammo.append ( Ammo ( ) )
            self.ammo_spawn_timer = current_time

        for ammo in self.ammo[:] :
            if ammo.rect.colliderect ( self.player.rect ) :
                self.player.bullets += 10
                self.ammo.remove ( ammo )

        for ammo in self.ammo[:] :
            if ammo.rect.left < 0 or ammo.rect.right > WIDTH or ammo.rect.top < 0 or ammo.rect.bottom > HEIGHT :
                self.ammo.remove ( ammo )

    def render(self) :
        self.screen.fill ( WHITE )
        pygame.draw.rect ( self.screen , GREEN , self.player.rect )
        for enemy in self.enemies :
            pygame.draw.rect ( self.screen , RED , enemy.rect )
        for bullet in self.bullets :
            pygame.draw.rect ( self.screen , BLUE , bullet.rect )
        for ammo in self.ammo :
            pygame.draw.rect ( self.screen , (255 , 215 , 0) , ammo.rect )  # Золотистый цвет для патронов

        font = pygame.font.SysFont ( None , 36 )
        score_text = font.render ( f'Score: {self.score}' , True , (0 , 0 , 0) )
        health_text = font.render ( f'Health: {self.player.health}' , True , (0 , 0 , 0) )
        bullets_text = font.render ( f'Bullets: {self.player.bullets}' , True , (0 , 0 , 0) )
        self.screen.blit ( score_text , (10 , 10) )
        self.screen.blit ( health_text , (10 , 40) )
        self.screen.blit ( bullets_text , (10 , 70) )

        pygame.display.flip ( )


if __name__ == "__main__" :
    init_db ( )  # Инициализируем БД
    game = Game ( )
    game.run ( )
